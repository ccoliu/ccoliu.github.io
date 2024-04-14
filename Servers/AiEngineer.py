'''This is the new program that is a ai engineer that can automatically generate code based on the problem description.'''

# Import necessary libraries
from openai import OpenAI  # OpenAI API
from bson import json_util  # For MongoDB may use the json_util

# Import self defined classes
from fileFormatt import StringToJsonl
from trainingClass import TrainingTool
from dataBase import dataBaseTools
import threading
import time
import random
import datetime

# Create instances of self defined classes
castTools = StringToJsonl()
fineTuneTools = TrainingTool()
dbTools = dataBaseTools()

# Read API keys from key file.
with open("key.txt", "r") as file:
    keys = file.readlines()

api_key_model_1 = keys[0].strip()
api_key_model_2 = keys[1].strip()
api_key_model_3 = keys[2].strip()

# Assign API keys to different models.
client_model_1 = OpenAI(api_key=api_key_model_1)  # Gpt-3.5-turbo-A
client_model_2 = OpenAI(api_key=api_key_model_2)  # Gpt-3.5-turbo-B
client_model_3 = OpenAI(api_key=api_key_model_3)  # Fine-Tuning-Model

BOSS = "You are a boss that is skilled at sperate the work into different parts and assign them to different people, you are good at managing the team and make sure the project is finished with high quality."

WORKSHEET_FORMAT = '''Worksheet\n
Main problem: Give me a maze game that can play at console.\n
(How many members are needed is up to you, since this is a one-way transfer, the roles cannot involve roles that require interactive communication. Each role will complete their work and then hand it off to the next person to continue. The smallest unit of task division is a function, meaning each person must be responsible for at least one function. Whether a person will need to handle more than one depends on the complexity of the function.)\n
Member role: You are a......\n
Member message:  Help me ......\n
Member role: You are a......\n
Member message:  Help me ......\n
Member role:  You are a......\n
Member message:  Help me ......\n
(The last one memeber should always be the one who can finish and combine all the tasks.)
Member role:  You are tasks combiner.\n
Member message:  Help me combine all the finished tasked before and make sure it solved the problem, simply print out the code part no need to describe the process.\n
etc.\n
'''


def createWorkSheet(inputPorblem, selected_language):
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
                + "How many members are needed to complete this task, as well as the roles and messages of each member, is up to you, but the output format must comply with the above."
                + "\n"
                + "The problem is:\n"
                + inputPorblem
                + "\n"
                + "Please make sure all the team members use the language: "
                + selected_language
                + "\n",
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
                "content": "Here is the main probelm"
                + problem
                + '\n'
                + "Here is the previos progess:\n"
                + previosOutput
                + '\n'
                + messages
                + '\n'
                + "Please finish the your part based on the main problem and previous output and add it to the program then pass the whole program to the next person.",
            },
        ],
    )

    print(currentAns.choices[0].message.content)

    return currentAns.choices[0].message.content


def recursiveAiEngineers(problem, roles, messages, previousOutput, index=0):
    if index < len(roles):
        newOutput = aiEngineers(problem, roles[index], messages[index], previousOutput)
        return recursiveAiEngineers(problem, roles, messages, newOutput, index + 1)
    else:
        return previousOutput


p = "give me a fibnacii sequence generator"
c = "print out 1 to 10 in python."
temp = createWorkSheet(c, "Python")

roles = []
messages = []
mainProblem = ""
getWorkSheetContent(temp, roles, messages, mainProblem)

finalOuput = recursiveAiEngineers(mainProblem, roles, messages, "None", 0)

print("Final Output:", finalOuput)
