'''This file is the server for the Code Assistance project. It is responsible for processing the code received from the frontend and returning the processed result to the frontend.'''

# Import necessary libraries
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS
import ssl  # Local https key
from bson import ObjectId

# Import self defined classes
from fileFormatt import StringToJsonl
from trainingClass import TrainingTool
from dataBase import dataBaseTools

# Set up SSL key for Flask to use https.
cert_path = 'C:/Users/whps9/ccoliu.github.io/certificate.crt'
key_path = 'C:/Users/whps9/ccoliu.github.io/private_key.key'

# Set the server type to https or http
SERVER_TYPE = "http"

# Create a Flask app
app = Flask(__name__)
CORS(app)

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


# Define system roles and their instructions.
interpreter = 'You are a master of sentence comprehension. When you receive language in various forms, you organize its requests into a bulleted list. For example: "I want a program that can perform addition and subtraction and output the result to the screen." Response: 1. Addition and subtraction functionality 2. Output the result to the screen.'

codeGenerater = "You are a program generator that produces programs based on bulleted lists of requirements. If the list of requirements is incomplete, you will automatically fill in the essential functions and annotate them with comments. Use the language:"

analyst = "You are a program issue analyst, adept at identifying potential problems by observing code. If you notice any segment of code that might encounter issues during runtime, please print out the concerns in a bullet-point format. If you find no issues, simply print out the phrase 'No issues'. If there exist issues, respond with a bullet-point list."

codeMaster = "You are a coding master, skilled at helping others modify their source code to ensure it runs correctly. If you receive only the source code, you will directly make corrections. If you receive both the source code and a list of potential issues, you will compare each item against the source code and analyze whether these issues may occur. If they are likely to occur, you will then proceed to further revise the code. You will return the source code that you generate or if there are no issues, you will return the original source code, no need to explain what you have done, just return the code."

reversedDiscriber = "You are a reverse engineer, capable of understanding the source code and diescribing its functionality or what this code is doing in sentences."


# This function will transfer user's request into bulleted list
def analyzeUserInput(inputSentence):
    analyzeInput = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": interpreter,
            },
            {
                "role": "user",
                "content": inputSentence,
            },
        ],
    )
    print(analyzeInput.choices[0].message.content)
    return analyzeInput.choices[0].message.content


# This function will generate code according to the bullet list
def generateCode(requirement, lang):
    generateResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": codeGenerater + lang,
            },
            {
                "role": "user",
                "content": requirement,
            },
        ],
    )
    print(generateResult.choices[0].message.content)
    return generateResult.choices[0].message.content


# This function may return a issues list or no issues.
def analyzeCode(inputCode):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": analyst,
            },
            {
                "role": "user",
                "content": inputCode,
            },
        ],
    )
    print(analyzeResult.choices[0].message.content)
    return analyzeResult.choices[0].message.content


def optimizeCode(inputCode, problemList):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": codeMaster,
            },
            {
                "role": "user",
                "content": "Here is the source code\n"
                + inputCode
                + "Here are the problems that may occur\n"
                + problemList,
            },
        ],
    )
    print(analyzeResult.choices[0].message.content)
    return analyzeResult.choices[0].message.content


def describeCode(inputCode):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": reversedDiscriber,
            },
            {
                "role": "user",
                "content": inputCode,
            },
        ],
    )
    print(analyzeResult.choices[0].message.content)
    return analyzeResult.choices[0].message.content


# Display the server's web page use for debugging.
@app.route("/", methods=["GET"])
def index():
    helloWorld = "Welcome! This is the Code Assistance's Server home page!"
    return helloWorld


# Process the code received from the frontend.
# Use for modify mode.
@app.route("/process_code", methods=["POST"])
def process_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        problems = analyzeCode(code)

        optimizedCode = optimizeCode(code, problems)

        summary = describeCode(optimizedCode)

        dataId = dbTools.insertModifyDocument(
            "fineTune", "modifiedCollection", code, optimizedCode, summary
        )

        print(optimizedCode + "\n")

        output = f"{optimizedCode}"
        # Return the processed result to the frontend
        return jsonify({"result": output, "id": str(dataId)})
    except Exception as e:
        return jsonify({"error": str(e)})


# Process the code received from the frontend.
# Use for generate mode.
@app.route("/gen_code", methods=["POST"])
def gen_code():
    try:
        data = request.get_json()
        userInput = data.get("code", "")

        lang = data.get("lang", "")
        targetLanguage = f"{lang}"

        # Turn user input into list
        requirmentList = analyzeUserInput(userInput)
        # Generate code in specific language
        genResult = generateCode(requirmentList, targetLanguage)

        summary = describeCode(genResult)

        dataId = dbTools.insertGenerateDocument(
            "fineTune", "generateCollection", userInput, requirmentList, genResult, summary
        )

        print(genResult + "\n")

        output = f"{genResult}"
        # Return the processed result to the frontend
        return jsonify({"result": output, "id": str(dataId)})
    except Exception as e:
        return jsonify({"error": str(e)})


# Process the code received from the frontend.
# Use for receiving comments.
@app.route("/retrieve_comment", methods=["POST"])
def retreive_code():
    try:
        data = request.get_json()

        rate = data.get("rate", "")
        comment = data.get("comment", "")
        id = data.get("id", "")

        idFilter = {'_id': ObjectId(id)}
        dbTools.updateDocument("fineTune", "generateCollection", idFilter, "rate", rate)
        dbTools.updateDocument("fineTune", "generateCollection", idFilter, "comment", comment)

        return jsonify({"result": "success"})
    except Exception as e:
        return jsonify({"error": str(e)})


# Process the code received from the frontend.
# Use for searching records.
@app.route("/communitySearch", methods=["POST"])
def search():
    try:
        data = request.get_json()
        # Get the keyword from the frontend
        keyword = data.get("keyword", "")

        idArray = []
        idArray = dbTools.communitySearch("fineTune", "codoctopus", keyword)

        return jsonify({"result": idArray})
    except Exception as e:
        return jsonify({"error": str(e)})


# Condtion to pick which server to use.
if SERVER_TYPE == "http":
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
elif SERVER_TYPE == "https":
    if __name__ == "__main__":
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        app.run(host='0.0.0.0', port=5000, ssl_context=context)
