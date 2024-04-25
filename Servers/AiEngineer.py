'''This is the Ai Engineer that can divide a project into several tasks and assign to several people to finish the project. The Ai Engineer will generate the worksheet for the team to solve the problem and assign the roles to the team members. The Ai Engineer will also inspect the progress of the project and fix the problem if there is any. The Ai Engineer will also combine all the tasks and adjust the variable name to make sure the program runs correctly'''

# For Flask server
from flask import Flask, request, jsonify  # Flask interface
from flask_cors import CORS

# Import necessary libraries
from openai import OpenAI  # OpenAI API
import os
import time
import threading
import random

# May be use for pharallel processing
import asyncio
import aiohttp

# Read API keys from key file.
with open("key.txt", "r") as file:
    keys = file.readlines()

api_key_model_1 = keys[0].strip()
api_key_model_2 = keys[1].strip()
api_key_model_3 = keys[2].strip()

# Assign API keys to different models should use for the dived job.
client_model_1 = OpenAI(api_key=api_key_model_1)  # Gpt-3.5-turbo-A
client_model_2 = OpenAI(api_key=api_key_model_2)  # Gpt-3.5-turbo-B
client_model_3 = OpenAI(api_key=api_key_model_3)  # Fine-Tuning-Model

# Create a Flask app
app = Flask(__name__)
CORS(app)

# Define some fixed roles of the gpt.
BOSS = "You are a software company boss that is skilled at divided the work into different parts and assign them to different people, and you are really good at managing the team and make sure the project is finished with high quality and meet the main target."

INSEPECTER = "You are a project inspector, you will have the main goal (or target) and the current progress of the project, you will inspect in any time and find out if there is any problem may lead to an error, if you find any, you will fix it and return the correct output, if there is no problem, you will simply return the current progress (only check on the job that had been done, don't care about the tasks that will be done at the future)."

FINAL_PICKER = "You are the last person who is responsible for picking out the program (code) part of the message and print it out in specific format."

# Define some format below #
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

FINAL_OUTPUT_FORMAT = '''
Main target:(Always put the main problem here)\n
Language used:(Always put the language used here)\n
Final output:\n
(Add the code here. Usually is the Program pool's content.)
'''

GROUP_FORMAT = '''GROUPS_START\n
(the content is just an example)
(Group and the following tasks should always be in same line)
Group 1: ['help me print 1 to 5', 'help me print 6 to 10', 'help me print 11 to 20', 'help me print 21 to 30', 'help me print 31 to 40']
Group 2: ['hele me comebine the functions']
Group 3: ['help me test the final program', 'help me test all the functions']
(how many groups is up to you, but the output format must comply with the above.)
GROUPS_END\n
'''
FORMAT_TOKEN = "You should return in the following format:\n"


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
def inspecterCheck(currentProgress, mainProblem, jobMatrix):
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
                + "If you find any probelm that might lead to an error, you will fix it and return the full program with the new code you adjusted, if there is no problem, you will simply return the full program you got.\n"
                + "No matter what you have or have not done, you should always return the current progress in the following foramt.\n"
                + MESSAGE_FORMAT,
            },
        ],
    )

    # Use to debug the output
    # print(inspectResult.choices[0].message.content)

    return inspectResult.choices[0].message.content


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

    # print("Main Problem:", mainProblem)
    # print("Member Messages:", messages)

    return mainProblem


# This is the main API of the Ai Engineer, every little job is done by this function.
def aiEngineers(mainTarget, systemRole, jobContent, inputProgress):
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
    print("Current Progress: ", currentProgress)
    return aiOutput.choices[0].message.content


# This function will analyze the job content and assign the group of each job.
def getTasksGroup(jobArray, mainTarget):
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
                "content": "Here are the Jobs that need to be done:\n"
                + jobString
                + '\n'
                + "Here is the main target of the whole project\n"
                + mainTarget
                + "According to the main target, please group the jobs into same group if they can be executed at the same time, the jobs that need to be executed in sequence shouldn't be in the same group and the jobs that can be executed in parallel should be in same group.\n"
                + "Each group now becomes a larger job, and there is a definite sequence among groups. For instance, in group 1, there are some printing functions, while in group 2, the task is to combine these printing functions. In group 3, the task is to test the functions from group 2. This means that the contents of groups 1, 2, and 3 are interrelated with the contents of other groups.\n"
                + "The group number should be the legitimate order of the execution.\n"
                + FORMAT_TOKEN
                + GROUP_FORMAT,
            },
        ],
    )

    # Assign the output message to the gptGroupFormat
    gptGroupFormat = gptGroupFormat.choices[0].message.content

    return gptGroupFormat


# This function will format the final output to the frontend.
def finalFormatter(currentProgess, mainTarget):
    finalOutput = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": FINAL_PICKER,
            },
            {
                "role": "user",
                "content": "Here is the main target\n"
                + mainTarget
                + '\n'
                + "Here is the final message:\n"
                + currentProgess
                + '\n'
                + FORMAT_TOKEN
                + FINAL_OUTPUT_FORMAT,
            },
        ],
    )

    finalOutput = finalOutput.choices[0].message.content

    return finalOutput


# This recursive method is for the old sequential method that calls the engineer one by one.
def recursiveAiEngineers(problem, roles, messages, index=0):
    global currentProgress, threadStopFlag, monitor_thread

    if index < len(roles):
        currentProgress = aiEngineers(problem, roles[index], messages[index], currentProgress)
        return recursiveAiEngineers(problem, roles, messages, index + 1)
    else:
        # threadStopFlag = True
        # monitor_thread.join()
        return currentProgress


# This function is the inspecter that will randomly check the progress of the project and fix the problem if there is any.
def inspecter():
    global threadStopFlag, workSheet, mainProblem, currentProgress
    while not threadStopFlag:
        time.sleep(random.randint(5, 10))
        currentProgress = inspecterCheck(currentProgress, mainProblem, workSheet)
        print("Inspecter inspecting: ", currentProgress)
        if threadStopFlag:
            break


# Convert the tasks to the format that can be displayed on the frontend 'Job: ...... '
def convertToDisplayJob(inputJobArray):
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
            outputJobArray.append("Job:" + s)

    return outputJobArray


# Convert the tasks back to the format that can be read by gpt 'Help me ...... '
def reverseToGptMessages(inputJobArray):
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

    for f in jobArray:
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
                    + f
                    + "\n"
                    + "Please use one sencence to describe the role for this person.\n"
                    + "for example: You are a program tester, you will test the program and find out the problem and fix it.\n",
                },
            ],
        )

        tempRoles = tempMessages.choices[0].message.content
        gptRoles.append(tempRoles)

    return gptRoles


# This function will create the layer array for the jobs.
def assignLayers(jobGroup, jobArray):
    jobGroup = rewrite_group_string(jobGroup)
    jobArray = preprocess_job_array(jobArray)
    lines = jobGroup.split('\n')
    layerIndex = []
    for realJob in jobArray:
        for line in lines:
            if realJob in line:
                layerNumber = line.split(':')[0].split()[-1]
                layerIndex.append(int(layerNumber))
                break

    return layerIndex


def preprocess_job_array(jobArray):
    processed_array = []
    for job in jobArray:
        processed_job = job.replace(' ', '').lower()
        processed_array.append(processed_job)
    return processed_array


def rewrite_group_string(input_string):
    # 将输入的字符串按行分割成列表
    lines = input_string.strip().split('\n')

    # 处理每一行字符串
    rewritten_lines = []
    for line in lines:
        # 如果是 GROUPS_START 或 GROUPS_END，则直接添加到重写后的列表中
        if line.strip() in ['GROUPS_START', 'GROUPS_END']:
            rewritten_lines.append(line)
        else:
            # 检查是否存在冒号
            if ':' in line:
                # 处理 Group 行
                group_name, group_content = line.split(':', 1)
                group_content = group_content.replace('[', "['").replace(']', "']")
                group_content = group_content.replace("', '", "','")
                group_content = group_content.replace(' ', '').lower()
                rewritten_lines.append(f'{group_name.lower()}:{group_content}')
            else:
                # 如果没有冒号，则直接添加到重写后的列表中
                rewritten_lines.append(line)

    # 将重写后的列表重新组合成字符串
    rewritten_string = '\n'.join(rewritten_lines)
    return rewritten_string


# The job worker called by threads.
def jobWorker(mainTarget, role, job, inputProgress, barrier):
    global currentProgress
    # Call the single engineer to do the job.
    currentProgress = aiEngineers(mainTarget, role, job, inputProgress)

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

    # After all the task is done, the final output will be the current progress.
    return currentProgress


# Define the routes, this one is default route to display the server is running.
@app.route("/", methods=["GET"])
def index():
    helloWorld = "Welcome! This is the Codoctopus AI engineer server !"
    return helloWorld


# This route is for the frontend analysis the code and generate the worksheet for the team to solve the problem.
@app.route("/gen_code", methods=["POST"])
def gen_code():
    try:
        global mainProblem
        data = request.get_json()
        userInput = data.get("code", "")
        lang = data.get("lang", "")
        roles = []
        messages = []
        workSheet = createWorkSheet(userInput, lang)
        mainProblem = getWorkSheetContent(workSheet, roles, messages, mainProblem)
        messages = convertToDisplayJob(messages)
        return jsonify({"result": messages})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/execute_steps", methods=["POST"])
def execute_steps():
    try:
        global mainProblem, currentProgress
        data = request.get_json()
        # Should deal with the arrays that send back.
        newJobs = data.get('steps', [])
        newRoles = []
        newJobs = reverseToGptMessages(newJobs)
        newRoles = assignGptRoles(newJobs)
        taskGroup = getTasksGroup(newJobs, mainProblem)
        jobLayers = [1, 2]
        jobLayers = assignLayers(taskGroup, newJobs)
        finalOutputCode = startProcessing(mainProblem, newRoles, newJobs, jobLayers)

        # This must be done before sending the final output to the frontend.
        finalOutputCode = finalFormatter(finalOutputCode, mainProblem)

        return jsonify({"result": finalOutputCode})
    except Exception as e:
        return jsonify({"error": str(e)})


# @app.route("/execute_steps", methods=["POST"])
# def execute_steps():
#     try:
#         global mainProblem, currentProgress
#         data = request.get_json()
#         # Should deal with the arrays that send back.
#         newMessages = data.get('steps', [])
#         newRoles = []
#         newMessages = reverseToGptMessages(newMessages)
#         newRoles = assignGptRoles(newMessages)
#         finalOutputCode = recursiveAiEngineers(mainProblem, newRoles, newMessages, 0)

#         # This must be done before sending the final output to the frontend.
#         finalOutputCode = finalFormatter(finalOutputCode, mainProblem)

#         return jsonify({"result": finalOutputCode})
#     except Exception as e:
#         return jsonify({"error": str(e)})


currentProgress = ""
mainProblem = ""
'''START_Test Area'''
# a = [
#     'help me print 1 to 5',
#     'help me print 11 to 20',
#     'help me combine all the functions',
#     'help me test the final program',
#     'help me print 6 to 10',
# ]

# testRoles = assignGptRoles(a)
# temp = getTasksGroup(a, 'help me gernerate a maze game')
# temp = rewrite_group_string(temp)
# print(temp)
# layers = []
# layers = assignLayers(temp, a)
# print(layers)
# startProcessing(mainProblem, testRoles, a, currentProgress, layers)
# end_time = time.time()

# execution_time = end_time - start_time
# print(f"Execution time: {execution_time} seconds")

'''END_Test Area'''
'''START_Test Area 2'''
# threadStopFlag = False

# """ monitor_thread = threading.Thread(target=inspecter)
# monitor_thread.daemon = True
# monitor_thread.start()
#  """
'''END_Test Area 2'''
# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
