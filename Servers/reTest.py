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
import unittest

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

MESSAGE_FORMAT_V2 = '''
Main problem:
(Put the project main target here to understand what the user want to do.)
Current job:
(Put your work goals here.)
Current job output:
(Add your completed work here.)
'''


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

MESSAGE_FORMAT = '''
Main problem:
(Always put the main problem here)
Program pool:
(Add your completed work to the program pool.)
Current job:
(Put your work goals here.)
Current job output:
(Add your completed work here.)
'''


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


# This is the main API of the Ai Engineer, every little job is done by this function.
def employeeWork_V2(mainTarget, systemRole, jobContent, inputProgress):
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
                "content": "Here is mian target of the project\n"
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
    aiResponse = aiOutput.choices[0].message.content
    current_program_pool = testEnforcer.extract_section_content(inputProgress, "Program pool")
    current_job_output = testEnforcer.extract_section_content(aiResponse, "Current job output")

    if current_program_pool == "Warning: No content was found.":
        current_program_pool = ""

    combination_output = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Help me combine the content of two string without any adjustment.",
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

    finalOutput = testEnforcer.insert_section(
        aiResponse, "Program pool", combination_output.choices[0].message.content
    )
    # print(finalOutput)
    return finalOutput


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


def test_employeeWork_V2_multilayer():
    # Initialize the test environment
    current_progress = '''
Main problem:
Develop a program that calculates the factorial of a given number using recursion.
Current job:
Current job output:
Program pool:
'''

    # Define the layers of tests
    layers = [
        {
            # Layer 1: Define the problem and start writing the basic factorial function
            "mainTarget": "Define the factorial function and implement a basic version.",
            "systemRole": "You are a software engineer. Your task is to create a basic implementation of the factorial function.",
            "jobContent": "Write a basic Python function to calculate the factorial of a given number using recursion.",
        },
        {
            # Layer 2: Add error handling to the factorial function
            "mainTarget": "Enhance the factorial function to include proper error handling.",
            "systemRole": "You are a software engineer skilled at improving code robustness.",
            "jobContent": "Add error handling to ensure the input is a non-negative integer, raising an appropriate error otherwise.",
        },
        {
            # Layer 3: Write test cases for the factorial function
            "mainTarget": "Develop comprehensive test cases for the factorial function.",
            "systemRole": "You are a software engineer experienced in writing test cases.",
            "jobContent": "Write unit tests for the factorial function, covering valid inputs (e.g., 0, 1, positive integers) and invalid inputs (e.g., negative numbers, non-integers).",
        },
        {
            # Layer 4: Optimize the test cases for edge cases
            "mainTarget": "Optimize test cases to cover all edge cases.",
            "systemRole": "You are a software engineer specializing in edge case testing.",
            "jobContent": "Optimize the test cases to cover edge cases such as very large numbers and ensure the function performs efficiently.",
        },
        {
            # Layer 5: Review and suggest improvements to the factorial function and test cases
            "mainTarget": "Review the factorial function and the test cases.",
            "systemRole": "You are a senior software engineer. Your task is to review the code and suggest improvements.",
            "jobContent": "Review the factorial function and its test cases, and suggest or implement improvements for clarity, performance, and maintainability.",
        },
    ]

    # Execute each layer
    for idx, layer in enumerate(layers, 1):
        # print(f"--- Running Layer {idx} ---")
        current_progress = employeeWork_V2(
            layer["mainTarget"],
            layer["systemRole"],
            layer["jobContent"],
            current_progress,
        )
        # print("\nUpdated Progress:\n", current_progress)

    return current_progress


final_pool = testEnforcer.extract_section_content(test_employeeWork_V2_multilayer(), "Program pool")
final_out = tidyUpProgramPool(
    "Develop a program that calculates the factorial of a given number using recursion", final_pool
)

print(final_out)
