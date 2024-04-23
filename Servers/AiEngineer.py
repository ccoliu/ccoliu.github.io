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

TASK_LAYER_FORMAT = '''LAYERS:[firstJobLayer, secondJobLayer, thirdJobLayer, ...(use numbers)]\n'''

GROUP_FORMAT = '''GROUPS_START\n
(the content is just an example)
Group 1: ['help me print 1 to 5', 'help me print 6 to 10', 'help me print 11 to 20', 'help me print 21 to 30', 'help me print 31 to 40']
Group 2: ['hele me comebine the functions']
Group 3: ['help me test the final program', 'help me test all the functions']
(how many groups is up to you, but the output format must comply with the above.)
GROUPS_END\n
'''
FORMAT_TOKEN = "You should return in the following format:\n"


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
                + "How many members are needed to complete this project, as well as the messages of each member, is up to you, but the output format must comply with the above."
                + "\n"
                + "The main target (request) is:\n"
                + request
                + "\n"
                + "Please make sure all the team members is using the language: "
                + language
                + "\n",
            },
        ],
    )

    # Print function for testing
    print(workSheet.choices[0].message.content)

    return workSheet.choices[0].message.content


def inspecterCheckPoint(currentProgress, mainProblem, workSheet):
    workSheet = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": INSEPECTER,
            },
            {
                "role": "user",
                "content": "Here is the main goal\n"
                + mainProblem
                + '\n'
                + "Here is the workSheet\n"
                + workSheet
                + "Here is the current progress:\n"
                + currentProgress
                + '\n'
                + "If you find any probelm that might lead to an error, you will fix it and return the full program with the new code you adjusted, if there is no problem, you will simply return the full program you got.",
            },
        ],
    )

    print(workSheet.choices[0].message.content)

    return workSheet.choices[0].message.content


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

    print("Main Problem:", mainProblem)
    print("Member Messages:", messages)

    return mainProblem


def aiEngineers(problem, roles, messages, previousMessage):
    output = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": roles,
            },
            {
                "role": "user",
                "content": "Here is the main probelm\n"
                + problem
                + '\n'
                + "Here is the previos message:\n"
                + previousMessage
                + '\n'
                + messages
                + '\n'
                + FORMAT_TOKEN
                + MESSAGE_FORMAT,
            },
        ],
    )

    print(output.choices[0].message.content)

    return output.choices[0].message.content


async def asyncAiEngineers(problem, roles, messages, previousMessage):
    output = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": roles,
            },
            {
                "role": "user",
                "content": "Here is the main probelm\n"
                + problem
                + '\n'
                + "Here is the previos message:\n"
                + previousMessage
                + '\n'
                + messages
                + '\n'
                + FORMAT_TOKEN
                + MESSAGE_FORMAT,
            },
        ],
    )

    return output.choices[0].message.content


# This function will analyze the messages and assign the layer to it.
def getTasksLayer(messages, mainProblem):
    jobs_str = str(messages)
    jobs_str = f"JOBS: {jobs_str}"

    print(jobs_str)
    tempOutput = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a task classifier, and you will group tasks that can be executed simultaneously into the same category and assign an order to ensure a plan can proceed smoothly.",
            },
            {
                "role": "user",
                "content": "Here is the main target of the project\n"
                + mainProblem
                + '\n'
                + "Here are the Jobs that should be assign:\n"
                + jobs_str
                + '\n'
                + "Please assign the layer to the jobs in the following logic:\n"
                + "If the input job list is JOBS: ['help me print 1 to 5', 'help me print 6 to 10', 'hele me comnebine the print functions', 'help me test the final program', 'help me print 11 to 20'] \n"
                + "The logic should be:\n"
                + "Tasks that can be executed simultaneously:'help me print 1 to 5''help me print 6 to 10''help me print 11 to 20' These tasks involve printing different ranges of numbers and have no dependencies on each other, so they can be executed in parallel. Tasks that need to be executed in sequence: 'help me combine the print functions' 'help me test the final program'"
                + "The output should be:\n"
                + "LAYERS:[1, 1, 2, 3, 1]\n"
                + "Now please help me assign the layer to the jobs in the following format:\n"
                + FORMAT_TOKEN
                + TASK_LAYER_FORMAT,
            },
        ],
    )

    tempOutput = tempOutput.choices[0].message.content

    numbers_str = tempOutput[tempOutput.index('[') + 1 : tempOutput.index(']')]

    numbers_list_str = numbers_str.split(',')

    numbers_list = [int(num) for num in numbers_list_str]

    return numbers_list


# This function will analyze the messages and assign the layer to it.
def getTasksGroup(messages, mainTarget):
    # Divide the jobs array into strings.
    jobs_str = str(messages)
    jobs_str = f"JOBS: {jobs_str}"
    print(jobs_str)

    tempOutput = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a Job classifier.",
            },
            {
                "role": "user",
                "content": "Here are the Jobs that need to be done:\n"
                + jobs_str
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

    tempOutput = tempOutput.choices[0].message.content

    return tempOutput


def finalFormatter(messages, mainProblem):
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
                + mainProblem
                + '\n'
                + "Here is the final message:\n"
                + messages
                + '\n'
                + FORMAT_TOKEN
                + FINAL_OUTPUT_FORMAT,
            },
        ],
    )

    return finalOutput.choices[0].message.content


def recursiveAiEngineers(problem, roles, messages, index=0):
    global currentProgress, threadStopFlag, monitor_thread
    print("Degug")
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
        currentProgress = inspecterCheckPoint(currentProgress, mainProblem, workSheet)
        print("Inspecter inspecting: ", currentProgress)
        if threadStopFlag:
            break


# This function will convert the message to the format that can be displayed on the frontend 'Job: ...... '
def convertToDisplayJob(innermessages):
    outputMessages = []
    for s in innermessages:
        # Format the message to lowercase
        lower_case_message = s.casefold()
        if lower_case_message.startswith("help me"):
            # replace the "help me" with "Job:"
            replaced_message = s.replace("Help me", "Job:", 1)
            replaced_message = replaced_message.replace("HELP ME", "Job:", 1)
            replaced_message = replaced_message.replace("help me", "Job:", 1)
            outputMessages.append(replaced_message)
        else:
            # If the output is not start with "help me", then add "Job:" to the beginning of the message.
            outputMessages.append("Job: " + s)

    return outputMessages


# This function will convert the message back to the original format 'Help me ...... '
def reverseToGptMessages(innermessages):
    outputMessages = []

    for s in innermessages:
        # Format the message to lowercase
        lower_case_message = s.casefold()
        if lower_case_message.startswith("job: "):
            # replace the "help me" with "Job:"
            replaced_message = s.replace("Job: ", "Help me", 1)
            replaced_message = replaced_message.replace("JOB: ", "Help me", 1)
            replaced_message = replaced_message.replace("job: ", "Help me", 1)
            outputMessages.append(replaced_message)
        else:
            # If the output is not start with "help me", then add "Job:" to the beginning of the message.
            outputMessages.append("Help me " + s)

    return outputMessages


def assignGptRoles(finalMessages):
    finalRoles = []

    for f in finalMessages:
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

        tempRple = tempMessages.choices[0].message.content
        finalRoles.append(tempRple)

    return finalRoles


def assignLayers(job_matrix, real_job_matrix):
    lines = job_matrix.split('\n')
    group_numbers = []
    for realJob in real_job_matrix:
        for line in lines:
            if realJob in line:
                group_number = line.split(':')[0].split()[-1]
                group_numbers.append(group_number)
                break

    return group_numbers


currentProgress = ""
mainProblem = "test"

# threadStopFlag = False

# """ monitor_thread = threading.Thread(target=inspecter)
# monitor_thread.daemon = True
# monitor_thread.start()
#  """
a = [
    'help me print 1 to 5',
    'help me print 6 to 10',
    'hele me comebine the functions',
    'help me test the final program',
    'help me print 11 to 20',
    'help me print 21 to 30',
    'help me test all the functions',
]

temp = getTasksGroup(a, 'print 1 to 30')

print(temp)

layers = []

layers = assignLayers(temp, a)

print(layers)


# Define the routes, this one is default route to display the server is running.
@app.route("/", methods=["GET"])
def index():
    helloWorld = "Welcome! This is the Codoctopus ai engineer server test!"
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
        newMessages = data.get('steps', [])
        newRoles = []
        newMessages = reverseToGptMessages(newMessages)
        newRoles = assignGptRoles(newMessages)
        finalOutputCode = recursiveAiEngineers(mainProblem, newRoles, newMessages, 0)
        finalOutputCode = finalFormatter(finalOutputCode, mainProblem)
        return jsonify({"result": finalOutputCode})
    except Exception as e:
        return jsonify({"error": str(e)})


# Run the server
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
