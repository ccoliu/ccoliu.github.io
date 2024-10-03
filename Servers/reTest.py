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


print(
    testEnforcer.strictlyFollowFormat(
        createWorkSheet,
        testEnforcer.is_valid_worksheet_format,
        "Create a program that can move a player around using console",
        "C++",
    )
)
