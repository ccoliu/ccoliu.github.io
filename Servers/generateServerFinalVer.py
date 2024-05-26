import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# For Flask server
from flask import Flask, request, jsonify  # Flask interface
from flask_cors import CORS

# Import necessary libraries
from openai import OpenAI  # OpenAI API
import os
import time
import threading
import random
import ssl  # Local https key

from dataBase import dataBaseTools

dbTools = dataBaseTools()

# Read API keys from key file using resource_path function
key_file_path = resource_path("key.txt")
with open(key_file_path, "r") as file:
    keys = file.readlines()

api_key_model_1 = keys[0].strip()
api_key_model_2 = keys[1].strip()
api_key_model_3 = keys[2].strip()

# Assign API keys to different models should use for the dived job.
client_model_1 = OpenAI(api_key=api_key_model_1)  # Gpt-3.5-turbo-A
client_model_2 = OpenAI(api_key=api_key_model_2)  # Gpt-3.5-turbo-B
client_model_3 = OpenAI(api_key=api_key_model_3)  # Fine-Tuning-Model

# Set up SSL key for Flask to use https.
cert_path = resource_path('C:/Users/whps9/ccoliu.github.io/certificate.crt')
key_path = resource_path('C:/Users/whps9/ccoliu.github.io/private_key.key')

# Set the server type to https or http
SERVER_TYPE = "http"

# Create a Flask app
app = Flask(__name__)
CORS(app)

# Define some fixed ROLES for GPT.
BOSS = "You are a software company boss that is skilled at divided the work into different parts and assign them to different people, and you are really good at managing the team and make sure the project is finished with high quality and meet the main target."

INSEPECTER = "You are a project inspector, you will have the main goal (or target) and the current progress of the project, you will inspect in any time and find out if there is any problem may lead to an error, if you find any, you will fix it and return the correct output, if there is no problem, you will simply return the current progress (only check on the job that had been done, don't care about the tasks that will be done at the future)."

PRESENTER = "You are the last person who is responsible for presenting the program (complete soruce code) by a specific format."

REVERSE_DISCRIBER = "You are a reverse engineer, capable of understanding the source code and discribing its' functionality or what this code is doing in sentences."

# Define some output format below.
WORKSHEET_FORMAT = '''Worksheet\n
Main problem: (understand what the user want to do and put it here)\n
(How many members are needed is up to you, since this is a one-way transfer, the roles cannot involve roles that require interactive communication. Each role will complete their work and then hand it off to the next person to continue. The smallest unit of task division is a function, meaning each person must be responsible for at least one function. Whether a person will need to handle more than one depends on the complexity of the function.)\n]
(1st member)
Member message:  Help me ......\n
(2nd member)
Member message:  Help me ......\n
(3rd member)
Member message:  Help me ......\n
(... up to you)\n
(The second last one member should be a tester who can find out what may be wrong with the code and fixed it.)
Member message: Test the program to see if it reach the main problem, if not, fix it and return the new code.\n
(The last one memeber should always be the one who can finish and combine all the tasks.)
Member message: Help me combine all the finished tasked and adjust the variable name to make sure the program runs correctly, and make sure to solved the errors.\n
'''

MESSAGE_FORMAT = '''
Main problem:(Always put the main problem here)\n
Program pool:(Add your completed work to the program pool.)\n
Current job:(Put your work goals here.)\n
Current job output(Add your completed work here.):\n
'''

FRONTED_OUTPUT_FORMAT = '''
Main target:(Always put the main problem here)\n
Language used:(Always put the language used here)\n
Final output:\n
(Completed source code. Put the Program pool's content here.)
'''

GROUPED_FORMAT = '''GROUPS_START\n
(the content is just an example)
(Group and the following tasks should always be in same line)
Group 1: ['help me print 1 to 5', 'help me print 6 to 10', 'help me print 11 to 20', 'help me print 21 to 30', 'help me print 31 to 40']
Group 2: ['hele me comebine the functions']
Group 3: ['help me test the final program', 'help me test all the functions']
(how many groups is up to you, but the output format must comply with the above.)
GROUPS_END\n
'''

FORMAT_TOKEN = "You should return in the following format:\n"


# This function will read the code and decribe it in human language.
def describeCode(inputCode):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": REVERSE_DISCRIBER,
            },
            {
                "role": "user",
                "content": inputCode + "\n" + "Please summarize in 1 sentences with in 100 tokens.",
            },
        ],
        max_tokens=100,
    )

    # print(analyzeResult.choices[0].message.content)

    return analyzeResult.choices[0].message.content


# Use to creating the worksheet for the team to solve the problem.
def createWorkSheet(request, language):
    workSheet = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": BOSS,
            },
            {
                "role": "user",
                "content": "Please use the following format to create a worksheet for the team to solve the problem.\n"
                + WORKSHEET_FORMAT
                + "How many members are needed to complete this project, as well as the messages of each member, is up to you, but the output format must comply with the above.\n"
                + "The main target (request) is:\n"
                + request
                + "\n"
                + "Please make sure all the team members is using the language: "
                + language
                + "\n",
            },
        ],
    )

    # Use to debug the output
    # print(workSheet.choices[0].message.content)

    return workSheet.choices[0].message.content


# Use for inspecter to check the progress of the project and lead it to correctness.
def inspecterCheck(mainProblem, jobMatrix):
    global currentProgress
    print("Inspecter is inspecting: ", currentProgress)
    # Turn the job array into string.
    jobMatrixText = ' '.join(jobMatrix)

    inspectResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": INSEPECTER,
            },
            {
                "role": "user",
                "content": "Here is the main target\n"
                + mainProblem
                + '\n'
                + "Here is all the job that sould be done.\n"
                + jobMatrixText
                + "Here is the current progress:\n"
                + currentProgress
                + '\n'
                + "You should respond in the following format:\n"
                + MESSAGE_FORMAT
                + "If you find any probelm, please fix it and put the correct answer in the program pool and decribe what you had done in the current job, if you find no problem simply respond the 'current progress' content that you recieved. You should always ignore the job that will be done in the future, only check the job that had been done.\n",
            },
        ],
    )

    # Use to debug the output
    print(inspectResult.choices[0].message.content)

    currentProgress = inspectResult.choices[0].message.content

    return


# Use for getting the specific content from the worksheet.
def getWorkSheetContent(text, roles, messages, mainProblem):
    # Splitting the text into lines
    lines = text.strip().split('\n')

    # Initialize lists to hold the roles and messages
    for line in lines:
        if line.startswith("Main problem:"):
            mainProblem = line.split("Main problem:")[1].strip()
        elif line.startswith("Member role:"):
            roles.append(line.split("Member role:")[1].strip())
        elif line.startswith("Member message:"):
            messages.append(line.split("Member message:")[1].strip())

    return mainProblem


# This is the main API of the Ai Engineer, every little job is done by this function.
def employeeWork(mainTarget, systemRole, jobContent, inputProgress):
    global currentProgress
    aiOutput = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": systemRole,
            },
            {
                "role": "user",
                "content": "Here is the target of the project\n"
                + mainTarget
                + '\n'
                + "Here is the current progress:\n"
                + inputProgress
                + '\n'
                + jobContent
                + '\n'
                + FORMAT_TOKEN
                + MESSAGE_FORMAT,
            },
        ],
    )

    # Use to debug the output
    # print(aiOutput.choices[0].message.content)

    return aiOutput.choices[0].message.content


# This function will analyze the job content and assign the group of each job.
def groupingAllJobs(jobArray, mainTarget):
    # Divide the jobs array into strings.
    jobString = str(jobArray)
    jobString = f"JOBS: {jobString}"

    gptGroupFormat = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a Job classifier.",
            },
            {
                "role": "user",
                "content": "Here are the Jobs that need to be classify:\n"
                + jobString
                + '\n'
                + "Here is the main target of the project\n"
                + mainTarget
                + "According to the main target, please group the jobs into same group if they can be executed at the same time, the jobs that need to be executed in sequence shouldn't be in the same group and the jobs that can be executed in parallel should be in same group.\n"
                + "Each group now becomes a larger job, and there is a definite sequence among groups. For instance, in group 1, there are some printing functions, while in group 2, the task is to combine these printing functions. In group 3, the task is to test the functions from group 2. This means that the contents of groups 1, 2, and 3 are interrelated with the contents of other groups.\n"
                + "The group number should be the legitimate order of the execution.\n"
                + FORMAT_TOKEN
                + GROUPED_FORMAT,
            },
        ],
    )

    # Assign the output message to the gptGroupFormat
    gptGroupFormat = gptGroupFormat.choices[0].message.content

    return gptGroupFormat


# This function will format the final output to the frontend.
def finalOutputDisplayer(currentProgess, mainTarget):
    finalOutput = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": PRESENTER,
            },
            {
                "role": "user",
                "content": "Here is the main target\n"
                + mainTarget
                + '\n'
                + "Here is the final result:\n"
                + currentProgess
                + '\n'
                + FORMAT_TOKEN
                + FRONTED_OUTPUT_FORMAT,
            },
        ],
    )

    finalOutput = finalOutput.choices[0].message.content

    return finalOutput


# This function is the inspecter that will randomly check the progress of the project and adjust the error if there is any.
def inspecter():
    global threadStopFlag, workSheet, mainProblem, currentProgress
    while not threadStopFlag:
        time.sleep(random.randint(5, 10))
        currentProgress = inspecterCheck(currentProgress, mainProblem, workSheet)
        print("Inspecter inspecting: ", currentProgress)
        if threadStopFlag:
            break


# Convert the tasks to the format that can be displayed on the frontend 'Job: ...... '
def convertJobToFrontFormat(inputJobArray):
    outputJobArray = []

    for s in inputJobArray:
        # Format the message to lowercase
        lower_case_message = s.casefold()

        if lower_case_message.startswith("help me"):
            # replace the "help me" with "Job:"
            replaced_message = s.replace("Help me", "Job:", 1)
            replaced_message = replaced_message.replace("HELP ME", "Job:", 1)
            replaced_message = replaced_message.replace("help me", "Job:", 1)
            outputJobArray.append(replaced_message)
        else:
            # If the output is not start with "help me", then add "Job:" to the beginning of the message.
            outputJobArray.append("Job: " + s)

    return outputJobArray


# Convert the tasks back to the format that can be read by gpt 'Help me ...... '
def convertToBackFormat(inputJobArray):
    outputJobArray = []

    for s in inputJobArray:
        lower_case_message = s.casefold()

        if lower_case_message.startswith("job:"):
            replaced_message = s.replace("Job:", "Help me", 1)
            replaced_message = replaced_message.replace("JOB:", "Help me", 1)
            replaced_message = replaced_message.replace("job:", "Help me", 1)
            outputJobArray.append(replaced_message)
        else:
            outputJobArray.append("Help me" + s)

    return outputJobArray


# This function will help to create the new gpt role array after the user's operation.
def assignGptRoles(jobArray):
    gptRoles = []

    for jobContents in jobArray:
        tempMessages = client_model_1.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are very good at giving a role to the team members, you can assign the roles to the team members based on the job they need to do.",
                },
                {
                    "role": "user",
                    "content": "Here is the job:\n"
                    + jobContents
                    + "\n"
                    + "Please use one sencence to describe the role for this person.\n"
                    + "For example: You are a program tester, you will test the program and find out the problem and fix it.\n",
                },
            ],
        )

        currentJobRole = tempMessages.choices[0].message.content
        gptRoles.append(currentJobRole)

    return gptRoles


# This function will create the layer array for the jobs.
def assignLayers(jobGroup, jobArray):
    # Preprocess the jobGroup
    jobGroup = preprocessGroupString(jobGroup)
    # Preprocess the jobArray
    jobArray = preprocessJobArray(jobArray)

    groupStringLines = jobGroup.split('\n')
    layers = []

    for currentJob in jobArray:
        for line in groupStringLines:
            if currentJob in line:
                layerNumber = line.split(':')[0].split()[-1]
                layers.append(int(layerNumber))
                break

    return layers


# This function will deal with the job array to make sure there is no space in the job content.
def preprocessJobArray(jobArray):
    newJobArray = []

    for job in jobArray:
        processedJob = job.replace(' ', '').lower()
        newJobArray.append(processedJob)

    return newJobArray


# This function will deal with the group string to make sure there is no space in it.
def preprocessGroupString(inputGroupString):
    lines = inputGroupString.strip().split('\n')

    newLines = []
    for line in lines:
        if line.strip() in ['GROUPS_START', 'GROUPS_END']:
            newLines.append(line)
        else:
            if ':' in line:
                groupName, groupContent = line.split(':', 1)
                groupContent = groupContent.replace('[', "['").replace(']', "']")
                groupContent = groupContent.replace("', '", "','")
                groupContent = groupContent.replace(' ', '').lower()

                # Don't change the group name.
                newLines.append(f'{groupName.lower()}:{groupContent}')
            else:
                newLines.append(line)

    finalString = '\n'.join(newLines)
    return finalString


# The job worker called by threads.
def jobWorker(mainTarget, role, job, inputProgress, barrier):
    global currentProgress
    # Call the single engineer to do the job.
    currentProgress = employeeWork(mainTarget, role, job, inputProgress)

    # Wait for all the threads to finish the job.
    barrier.wait()


# The main function to start the processing all of the jobs.
def startProcessing(mainTarget, roles, jobArray, layerIndex):
    # The shared variable to store the current progress of the project.
    global currentProgress

    # The thread pool to store all the threads in this layer.
    threads = []
    total_jobs = len(layerIndex)

    # Set the layer index to the set to avoid the duplicate layer.
    for layer in set(layerIndex):
        # Output the current info's
        print(f'Processing jobs in layer {layer}')

        jobLayers = [job for job, layerNumber in enumerate(layerIndex, 1) if layerNumber == layer]

        # Output the current info's
        print(f'Jobs in layer {layer}: {jobLayers}')

        # Build a Barrier object to synchronize the threads
        layer_barrier = threading.Barrier(len(jobLayers))

        for jobIndex in jobLayers:
            # Create the thread for each job.
            thread = threading.Thread(
                target=jobWorker,
                args=(
                    mainTarget,
                    roles[jobIndex - 1],
                    jobArray[jobIndex - 1],
                    currentProgress,
                    layer_barrier,
                ),
            )

            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        inspecterCheck(mainTarget, jobArray)
    # After all the task is done, the final output will be the current progress.
    return currentProgress


currentProgress = ""
mainProblem = ""


# Define the routes, this one is default route to display the server is running.
@app.route("/", methods=["GET"])
def index():
    helloWorld = "Welcome! This is the Code Assistance's Generate Server!"
    return helloWorld


# This route is for the frontend analysis the code and generate the worksheet for the team to solve the problem.
@app.route("/gen_code", methods=["POST"])
def gen_code():
    try:
        global mainProblem, originalTasks
        data = request.get_json()
        userInput = data.get("code", "")
        lang = data.get("lang", "")

        roles = []
        dividedJobs = []

        workSheet = createWorkSheet(userInput, lang)
        mainProblem = getWorkSheetContent(workSheet, roles, dividedJobs, mainProblem)
        dividedJobs = convertJobToFrontFormat(dividedJobs)

        originalTasks = dividedJobs
        return jsonify({"result": dividedJobs})
    except Exception as e:
        return jsonify({"error": str(e)})


# This route is for executing the steps that the team members have done.
@app.route("/execute_steps", methods=["POST"])
def execute_steps():
    try:
        global mainProblem, currentProgress
        data = request.get_json()
        # Should deal with the arrays that send back.
        newJobs = data.get('steps', [])
        newRoles = []

        newJobs = convertToBackFormat(newJobs)
        newRoles = assignGptRoles(newJobs)
        taskGroup = groupingAllJobs(newJobs, mainProblem)
        jobLayers = []
        jobLayers = assignLayers(taskGroup, newJobs)

        # Start the processing of the jobs.
        finalOutputCode = startProcessing(mainProblem, newRoles, newJobs, jobLayers)
        # This must be done before sending the final output to the frontend.
        finalOutputCode = finalOutputDisplayer(finalOutputCode, mainProblem)

        summary = describeCode(finalOutputCode)

        dataId = dbTools.insertGenerateData(
            "fineTune", "codoctopus", mainProblem, originalTasks, newJobs, finalOutputCode, summary
        )

        return jsonify({"result": finalOutputCode, "id": str(dataId)})
    except Exception as e:
        return jsonify({"error": str(e)})


# Condtion to pick which server to use.
if SERVER_TYPE == "http":
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5001)
elif SERVER_TYPE == "https":
    if __name__ == "__main__":
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        app.run(host='0.0.0.0', port=5001, ssl_context=context)
