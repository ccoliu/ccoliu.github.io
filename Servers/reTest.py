import re
import os  # System imports
import sys
import configparser  # For reading the config file (ini file)
from flask import Flask, request, jsonify, redirect, Response  # For Flask server
from flask_cors import CORS  # For Flask server
from openai import OpenAI  # OpenAI API
import time
import threading
import random

# Self-defined imports
from dataBase import dataBaseTools

import FormatEnforcer

testEnforcer = FormatEnforcer.Enforcer()


# Function to get the file path after packaging
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


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

# Define some output format below.
WORKSHEET_FORMAT = '''Worksheet
Main problem: (understand what the user want to do and put it here)
(How many members are needed is up to you, since this is a one-way transfer, the roles cannot involve roles that require interactive communication. Each role will complete their work and then hand it off to the next person to continue. The smallest unit of task division is a function, meaning each person must be responsible for at least one function. Whether a person will need to handle more 
Member message: Help me ......
Member message: Help me ......
Member message: Help me ......
(... up to you, and don't list the index of the member)
(The last two messages are fixed and cannot be changed)
Member message: Help me Test the program to see if it reach the main problem, if not, fix it and return the new code.
Member message: Help me combine all the finished tasked and adjust the variable name to make sure the program runs correctly, and make sure to solved the errors.
(Don't add any extra information, and don't change the format)
'''
BOSS = "You are a software company boss that is skilled at divided the work into different parts and assign them to different people, and you are really good at managing the team and make sure the project is finished with high quality and meet the main target."


FRONTED_OUTPUT_FORMAT = '''
Main target:
(Always describe the primary problem or task clearly here.)

Language use:
(Specify the programming language to be used, such as Python, C++, etc.)

Final output:
(Provide the completed source code here. In other word it's the progeram pool's content.)

Other comment:
(Add any additional notes, context, or requirements here that can help user to understand the code better.)
'''
FORMAT_TOKEN = "You should return in the following format:\n"
PRESENTER = "You are the last person who is responsible for presenting the program (complete soruce code) by a specific format."


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

    return workSheet.choices[0].message.content


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


# print(
#     testEnforcer.strictlyFollowFormat(
#         createWorkSheet,
#         testEnforcer.is_valid_worksheet_format,
#         "Create a program that can move a player around using console",
#         "C++",
#     )
# )


# TEST GenerateOutput Format
TEST = '''Main problem:
Develop a program that calculates the factorial of a given number using recursion.

Program pool:
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

print("Factorial of 5:", factorial(5))

Current job:
Finalize the program by adding proper error handling and user input validation.

Current job output:
def factorial(n):
    if not isinstance(n, int) or n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

try:
    num = int(input("Enter a number: "))
    print(f"Factorial of {num}: {factorial(num)}")
except ValueError as e:
    print("Error:", e)
'''
# print(
#     testEnforcer.strictlyFollowFormat(
#         finalOutputDisplayer,
#         testEnforcer.is_valid_generate_output_format,
#         TEST,
#         "Develop a program that calculates the factorial of a given number using recursion",
#     )
# )
