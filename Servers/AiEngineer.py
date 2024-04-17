'''This is a ai engineer that can divide a job into several tasks and finshed it self.'''

# For testing the server.
from flask import Flask, request, jsonify  # Flask interface
from flask_cors import CORS

# Import necessary libraries
from openai import OpenAI  # OpenAI API
import os
import time
import threading
import random

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

BOSS = "You are a software company boss that is skilled at divided the work into different parts and assign them to different people, and you are really good at managing the team and make sure the project is finished with high quality and meet the main target."

INSEPECTER = "You are a project inspector, you will have the main goal (or target) and the current progress of the project, you will inspect in any time and find out if there is any problem may lead to an error, if you find any, you will fix it and return the correct output, if there is no problem, you will simply return the current progress (only check on the job that had been done, don't care about the tasks that will be done at the future)."

# Define some format below #
WORKSHEET_FORMAT = '''Worksheet\n
Main problem: Give me a maze game that can play at console.\n
(How many members are needed is up to you, since this is a one-way transfer, the roles cannot involve roles that require interactive communication. Each role will complete their work and then hand it off to the next person to continue. The smallest unit of task division is a function, meaning each person must be responsible for at least one function. Whether a person will need to handle more than one depends on the complexity of the function.)\n
Member role: You are a......\n
Member message:  Help me ......\n
Member role: You are a......\n
Member message:  Help me ......\n
Member role:  You are a......\n
Member message:  Help me ......\n
(The second last one member should be a tester who can find out what may be wrong with the code and fixed it.)
Member role:  You are a program tester if you figure out some problem in the code, you fix it and simply return the new code.\n
Member message: Test the program to see if it reach the main problem, if not, fix it and return the new code.\n
(The last one memeber should always be the one who can finish and combine all the tasks.)
Member role:  You are tasks combiner.\n
Member message:  Help me combine all the finished tasked before and make sure it solved the problem, simply print out the code part no need to describe the process.\n
etc.\n
'''

MESSAGE_FORMAT = '''
Main problem:(Put the main problem here)\n
Program pool:(Add your completed work to the program pool.)\n
Current job:(Put your work goals here.)\n
Current job output(Add your completed work here.):\n
'''

OUTPUT_TOKEN = "You should return in the following format:\n"


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
                + "How many members are needed to complete this project, as well as the roles and messages of each member, is up to you, but the output format must comply with the above."
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
    print("Member Roles:", roles)
    print("Member Messages:", messages)


def aiEngineers(problem, roles, messages, previosOutput):
    currentAns = client_model_1.chat.completions.create(
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
                + "Here is the previos progess:\n"
                + previosOutput
                + '\n'
                + messages
                + '\n'
                + "Please finish the your part based on the main problem and previous output, and add it to the program then pass the whole program to the next person, do not omit any part of the program, just add your part to the end of the program.",
            },
        ],
    )

    print(currentAns.choices[0].message.content)

    return currentAns.choices[0].message.content


def aiEngineersVer2(problem, roles, messages, previousMessage):
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
                + OUTPUT_TOKEN
                + MESSAGE_FORMAT,
            },
        ],
    )

    print(output.choices[0].message.content)

    return output.choices[0].message.content


def recursiveAiEngineers(problem, roles, messages, previousOutput, index=0):
    if index < len(roles):
        newOutput = aiEngineers(problem, roles[index], messages[index], previousOutput)
        return recursiveAiEngineers(problem, roles, messages, newOutput, index + 1)
    else:
        return previousOutput


def testRecursiveAiEngineers(problem, roles, messages, index=0):
    global currentProgress, threadStopFlag, monitor_thread
    if index < len(roles):
        currentProgress = aiEngineersVer2(problem, roles[index], messages[index], currentProgress)
        return testRecursiveAiEngineers(problem, roles, messages, index + 1)
    else:
        # threadStopFlag = True
        # monitor_thread.join()
        return currentProgress


def inspecter():
    global threadStopFlag, workSheet, mainProblem, currentProgress
    while not threadStopFlag:
        time.sleep(random.randint(5, 10))
        currentProgress = inspecterCheckPoint(currentProgress, mainProblem, workSheet)
        print("Inspecter inspecting: ", currentProgress)
        if threadStopFlag:
            break


# testA = "give me a fibnacii sequence generator"
# testB = "print out 1 to 10 in python."
# testC = "give me a maze game that can play at console."
# testD = "give me a program that can print out the prime numbers between 1 to 100."
# workSheet = createWorkSheet(testC, "python")

# roles = []
# messages = []
# mainProblem = ""
# currentProgress = ""
# getWorkSheetContent(workSheet, roles, messages, mainProblem)

# threadStopFlag = False

# """ monitor_thread = threading.Thread(target=inspecter)
# monitor_thread.daemon = True
# monitor_thread.start()
#  """
# # finalOuput = recursiveAiEngineers(mainProblem, roles, messages, "None", 0)
# # print("Final Output:", finalOuput)

# finalOutput = testRecursiveAiEngineers(mainProblem, roles, messages, 0)

# print("Final Output:", finalOutput)


@app.route("/", methods=["GET"])
def index():
    helloWorld = "Welcome! This is the Code Assistance's Server home page!"
    return helloWorld


@app.route("/gen_code", methods=["POST"])
def gen_code():
    try:
        data = request.get_json()
        userInput = data.get("code", "")
        lang = data.get("lang", "")
        roles = []
        messages = []
        mainProblem = ""
        workSheet = createWorkSheet(userInput, lang)
        getWorkSheetContent(workSheet, roles, messages, mainProblem)

        # finalOutput = testRecursiveAiEngineers(mainProblem, roles, messages, 0)
        # Return the processed result to the frontend
        return jsonify({"result": messages})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
