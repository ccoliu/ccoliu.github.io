# ---------------------------------------------------
# Author:Daniel Hsiao (Github: https://github.com/whps970083),  ccoliu (Github: https://github.com/ccoliu)
# Date: 2024/10/01
# Update: 2024/12/01
# Version: <V10.0.1.0>
# ---------------------------------------------------

# ---------------------------------------------------
'''Import the necessary libraries and modules'''
# ---------------------------------------------------

import os  # System imports
import sys
import configparser  # For reading the config file (ini file)
from flask import Flask, request, jsonify, redirect, Response  # For Flask server
from flask_cors import CORS  # For Flask server
from openai import OpenAI  # OpenAI API
import os
import time
import threading
import random
import ssl  # Local https key
import logging
from datetime import datetime

# ---------------------------------------------------
'''Import the self-defined tools and functions'''
# ---------------------------------------------------

import FormatEnforcer
from dataBase import dataBaseTools

# ---------------------------------------------------
'''System initialization and configuration'''
# ---------------------------------------------------


# Function to get the file path after packaging
def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Get the current path of the server
current_path = resource_path("")

# Create a Log folder if it does not exist
log_folder_path = os.path.abspath(current_path + "/Log")
if not os.path.exists(log_folder_path):
    os.makedirs(log_folder_path)  # Create the log folder
    print(f"Log folder created: {log_folder_path}")


# Dynamic log handler to switch log files daily
class DynamicLogHandler:
    def __init__(self, log_folder):
        self.log_folder = log_folder
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.setup_general_logger()
        self.setup_web_logger()

    def setup_general_logger(self):
        """Set up the logger for general stdout logs."""
        self.general_log_file = os.path.join(
            self.log_folder, f"{self.current_date}_gen_server_logs.log"
        )
        self.general_logger = logging.getLogger("general")
        self.general_logger.setLevel(logging.INFO)
        self.general_logger.handlers = []  # Clear previous handlers

        # File handler for logging to a file
        general_file_handler = logging.FileHandler(self.general_log_file, mode="a")
        general_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.general_logger.addHandler(general_file_handler)

        # Stream handler for logging to console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.general_logger.addHandler(console_handler)

    def setup_web_logger(self):
        """Set up the logger for werkzeug (web-related) logs."""
        self.web_log_file = os.path.join(
            self.log_folder, f"{self.current_date}_gen_server_web_logs.log"
        )
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.setLevel(logging.INFO)
        werkzeug_logger.handlers = []  # Clear previous handlers
        web_file_handler = logging.FileHandler(self.web_log_file, mode="a")
        web_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        werkzeug_logger.addHandler(web_file_handler)

    def check_date_and_rotate_logs(self):
        """Check the date and rotate log files if the date has changed."""
        new_date = datetime.now().strftime("%Y-%m-%d")
        if new_date != self.current_date:
            self.current_date = new_date
            self.setup_general_logger()
            self.setup_web_logger()


# Initialize the dynamic log handler
log_handler = DynamicLogHandler(log_folder_path)


# Custom stream handler to log only stdout to the general log file and console
class StreamToLogger:
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        if message.strip():
            log_handler.check_date_and_rotate_logs()  # Check and rotate logs if needed
            self.logger.info(message.strip())

    def flush(self):
        pass


# Redirect stdout to both console and general logger
sys.stdout = StreamToLogger(log_handler.general_logger)


# Initialize Tools
dbTools = dataBaseTools()
message_inforcer = FormatEnforcer.Enforcer()

# Initialize some variables
SERVER_TYPE = "https"

# Get current file path
current_path = os.path.dirname(os.path.realpath(__file__))
# Get the ini file path
config_file_path = os.path.join(current_path, "Config.ini")
# Get the config tool to manage the config file
config_tool = configparser.ConfigParser()

# Check if the config file exists
if not os.path.exists(config_file_path):
    raise FileNotFoundError(f"Config file not found at: {config_file_path}")
else:
    config_tool.read(config_file_path)
    # Get the connection type from the config file
    SERVER_TYPE = config_tool["ServerSettings"]["ConnectionType"]


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
cert_path = resource_path('certificate.crt')
key_path = resource_path('private_key.key')


# Create a Flask app
app = Flask(__name__)
CORS(app)

# ---------------------------------------------------
'''Define some necessary roles for the team members.'''
# ---------------------------------------------------

# This is the Boss of the team, who is responsible for dividing the work and assigning them to different people.
BOSS = "You are a software company boss that is skilled at divided the work into different parts and assign them to different people, and you are really good at managing the team and make sure the project is finished with high quality and meet the main target."
# This is the presenter, who is responsible for presenting the final output of the project.
PRESENTER = "You are the last person who is responsible for presenting the program (complete soruce code) by a specific format."
# This is the reverse engineer, who is responsible for understanding the source code and describing its functionality.
# Note: This person is use to describe the code in human language and put it in the database will be used for community search.
REVERSE_DISCRIBER = "You are a reverse engineer, capable of understanding the source code and discribing its' functionality or what this code is doing in sentences."

# ---------------------------------------------------
'''Define some output format below.'''
# ---------------------------------------------------

# Note the enforced format is done.
WORKSHEET_FORMAT = '''Worksheet
Main problem: (understand what the user want to do and put it here)
(How many members are needed is up to you, since this is a one-way transfer, the roles cannot involve roles that require interactive communication. Each role will complete their work and then hand it off to the next person to continue. The smallest unit of task division is a function, meaning each person must be responsible for at least one function. Whether a person will need to handle more)
Member message: Help me ......
Member message: Help me ......
Member message: Help me ......
(... up to you, and don't list the index of the member)
(The last two messages are fixed and cannot be changed)
Member message: Help me Test the program to see if it reach the main problem, if not, fix it and return the new code.
Member message: Help me combine all the finished tasked and adjust the variable name to make sure the program runs correctly, and make sure to solved the errors.
(Don't add any extra information, and don't change the format)
'''
# Note the enforced format is done.
MESSAGE_FORMAT = '''
Main problem:
(Always put the main problem here)
Program pool:
(Add your completed work to the here.)
Current job:
(Put your work goals here.)
Current job output:
(Add your completed work here.)
'''

MESSAGE_FORMAT_V2 = '''
Main problem:
(Put the project main target here to understand what the user want to do.)
Current job:
(Put your work goals here.)
Current job output:
(Add your completed work here.)
'''

# Note the enforced format is done.
FRONTED_OUTPUT_FORMAT = '''
Main target:
(Always describe the primary problem or task clearly here.)

Language use:
(Specify the programming language to be used, such as Python, C++, etc.)

Final output:
(Provide the completed source code here)

Other comment:
(Add any additional notes, context, or requirements here that can help user to understand the code better.)
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

# This phrase is use to place before the specific format.
FORMAT_TOKEN = '''You should return in the following format:\n'''

# ---------------------------------------------------
'''Define some functions below.'''
# ---------------------------------------------------


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
                "content": "Please strictly follow the format below to create a worksheet for the team to solve the problem.\n"
                + WORKSHEET_FORMAT
                + "How many members are needed to complete this project, as well as the messages of each member, is up to you, It is **required** that the output strictly follows the above format, and any deviations are unacceptable."
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
                + "Here is the last member's output:\n"
                + inputProgress
                + '\n'
                + jobContent
                + '\n'
                + FORMAT_TOKEN
                + MESSAGE_FORMAT,
            },
        ],
    )

    return aiOutput.choices[0].message.content


# This is the main API of the Ai Engineer, every little job is done by this function.
def enhancedEmployeeWork(mainTarget, systemRole, jobContent, inputProgress):
    ai_output = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": systemRole,
            },
            {
                "role": "user",
                "content": "Here is the main target of the project\n"
                + mainTarget
                + '\n'
                + "Here is the last member's progress for you to refer:\n"
                + inputProgress
                + '\n'
                + "Here is the job that you need to do:\n"
                + jobContent
                + '\n'
                + FORMAT_TOKEN
                + MESSAGE_FORMAT_V2,
            },
        ],
    )

    ai_response = ai_output.choices[0].message.content
    current_program_pool = message_inforcer.extract_section_content(inputProgress, "Program pool")
    current_job_output = message_inforcer.extract_section_content(ai_response, "Current job output")

    if current_program_pool == "Warning: No content was found.":
        current_program_pool = ""

    combined_output_request = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Help me combine the content of two strings without any adjustment.",
            },
            {
                "role": "user",
                "content": "Help me combine the following two strings:\n"
                + current_program_pool
                + '\n'
                + current_job_output
                + '\n'
                + "Simply combine them together without any adjustment.",
            },
        ],
    )

    combined_output = combined_output_request.choices[0].message.content
    final_output = message_inforcer.insert_section(ai_response, "Program pool", combined_output)

    return final_output


def tidyUpProgramPool(mainTarget, programPool):

    ai_output = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are responsible for tidying up the program pool. Ensure the source code meets the main target without any duplicate code.",
            },
            {
                "role": "user",
                "content": "Here is the main target of the project:\n"
                + mainTarget
                + '\n'
                + "Here is the program pool that contains all the code that has been done:\n"
                + programPool
                + '\n'
                + "Please tidy up the program pool to ensure it meets the main target and keep all the functions in the program pool."
                + "Only retrun the source code, don't add any extra information.",
            },
        ],
    )

    return ai_output.choices[0].message.content


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
                "content": "You are a Job classifier, you can unsderstand if the job is independent or dependent, and you can group the jobs that can be executed at the same time.",
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
    # MOD 20241201 Daniel Now use the enhancedEmployeeWork to do the job.
    currentProgress = enhancedEmployeeWork(mainTarget, role, job, inputProgress)
    # currentProgress = employeeWork(mainTarget, role, job, inputProgress)

    # Wait for all the threads to finish the job.
    barrier.wait()


# Variables for progress bar

progressBar_current = 0
progressBar_total = 0


# The main function to start the processing all of the jobs.
def startProcessing(mainTarget, roles, jobArray, layerIndex):
    # The shared variable to store the current progress of the project.
    global currentProgress, progressBar_current, progressBar_total

    # The thread pool to store all the threads in this layer.
    threads = []
    progressBar_total = len(jobArray) + 1
    progressBar_current = 0

    # Set the layer index to the set to avoid the duplicate layer.
    for layer in set(layerIndex):
        # Output the current info's
        print(f'Processing jobs in layer {layer}')

        jobLayers = [job for job, layerNumber in enumerate(layerIndex, 1) if layerNumber == layer]

        # Output the current info's
        print(f'Jobs in layer {layer}: {jobLayers}')

        for jobIndex in jobLayers:
            print(f"Job {jobIndex} content: {jobArray[jobIndex - 1]}")

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

        progressBar_current += len(jobLayers)

        for thread in threads:
            thread.join()

    # After all the task is done, the final output will be the current progress.
    return currentProgress


currentProgress = ""
mainProblem = ""


@app.route("/", methods=["GET"])
def index():
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return "Unblock generate mode successfully! Now you can reutrn to the previous page and start to generate the code."


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
        mainProblem += "Using the language: " + lang
        dividedJobs = convertJobToFrontFormat(dividedJobs)

        originalTasks = dividedJobs
        return jsonify({"result": dividedJobs})
    except Exception as e:
        return jsonify({"error": str(e)})


# This route is for executing the steps that the team members have done.
@app.route("/execute_steps", methods=["POST"])
def execute_steps():
    try:
        global mainProblem, currentProgress, progressBar_current, progressBar_total
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
        # ADD 20241201 Daniel Now use the tidyUpProgramPool to tidy up the program pool.

        # Get the Program pool first.
        final_prog_pool = message_inforcer.extract_section_content(finalOutputCode, "Program pool")
        finalOutputCode = tidyUpProgramPool(mainProblem, final_prog_pool)

        # Let AI to gerate the final output content.
        # finalOutputCode = finalOutputDisplayer(finalOutputCode, mainProblem)
        # Force the final output code to follow the format.
        finalOutputCode = message_inforcer.strictlyFollowFormat(
            finalOutputDisplayer,
            message_inforcer.is_valid_message_format,
            finalOutputCode,
            mainProblem,
        )

        # Finshed the progress bar.
        progressBar_current += 1

        time.sleep(1)
        summary = describeCode(finalOutputCode)

        dataId = dbTools.insertGenerateData(
            "fineTune", "codoctopus", mainProblem, originalTasks, newJobs, finalOutputCode, summary
        )

        return jsonify({"result": finalOutputCode, "id": str(dataId)})
    except Exception as e:
        return jsonify({"error": str(e)})


# SSE Streaming route
# This route is for the frontend to get the progress of the project.
@app.route('/stream')
def stream():
    def event_stream():
        # To get the global variable of cuurent progress and total progress.
        global progressBar_current, progressBar_total

        try:
            # Loop until the progress bar is full.
            while progressBar_current < progressBar_total or progressBar_total == 0:
                progress_message = f"{progressBar_current},{progressBar_total}\n"
                yield f"data: {progress_message}\n\n"
                # print('Progress:', progress_message)
                # Sleep for 2 seconds then continue the loop.
                time.sleep(2)

            # Since the last message won't be sent, we need to send the final message.
            progress_message = f"{progressBar_total},{progressBar_total}\n"
            yield f"data: {progress_message}\n\n"
            # print('Final Progress:', progress_message)

            # Make sure the last message is send before the return.
            time.sleep(1.5)
            return
        except GeneratorExit:
            print("Client disconnected gracefully.")
        except Exception as e:
            print(f"An error occurred: {e}")

        # The progress bar is done, so we need to reset the progress bar.
        finally:
            progressBar_total = 0
            progressBar_current = 0

    return Response(event_stream(), content_type='text/event-stream')


# Switch the server connection type
if SERVER_TYPE == "http":
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5001)
elif SERVER_TYPE == "https":
    if __name__ == "__main__":
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        app.run(host='0.0.0.0', port=56494, ssl_context=context)
