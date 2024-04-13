'''This is the file that keep generating the data for the auto fine tune server.'''

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


PROBLEM_GENERATER = "You are a random question asker who simply ask for code to solve your problem, for example 'give me a fibnacii sequence generator', 'give me a maze game', 'give me a code that can deal with any kind of file such as txt or csv'."

CODE_GENERATEER = "You are a code generator, you can generate code based on the problem description, for example 'generate a code that can deal with any kind of file such as txt or csv', 'generate a code that can deal with any kind of file such as txt or csv'."


def generateProblem():
    problem = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": PROBLEM_GENERATER,
            },
            {
                "role": "user",
                "content": "Give me a random problem that can be solved by code.",
            },
        ],
    )

    print(problem.choices[0].message.content)

    return problem.choices[0].message.content


def generateCode(inputProblem, selected_language):
    aiCode = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": PROBLEM_GENERATER,
            },
            {
                "role": "user",
                "content": inputProblem
                + "Use language "
                + selected_language
                + " to generate the code to sovle the problem and the first line of the code should be the language you use.\n"
                + "No need to explain the code, just generate the code.",
            },
        ],
    )

    print(aiCode.choices[0].message.content)

    return aiCode.choices[0].message.content


def getFirstLine(inputText):
    # Split the input text into lines
    lines = inputText.splitlines()
    # Return the first line
    return lines[0] if lines else None


def generate_random_language():
    # List of programming languages
    languages = [
        'Python',
        'Java',
        'C++',
        'C',
        'C#',
        'JavaScript',
        'Ruby',
        'Go',
        'Rust',
        'Swift',
        'Kotlin',
        'TypeScript',
    ]
    weights = list(range(len(languages), 0, -1))

    selected_language = random.choices(languages, weights=weights, k=1)[0]

    return selected_language


# Generate a random problem
problem = generateProblem()
# Generate a random language
selected_language = generate_random_language()
# Generate code to solve the problem using the selected language
code = generateCode(problem, selected_language)

dbTools.insertGptCode("fineTune", "gptGenerateCode", problem, code, selected_language)
