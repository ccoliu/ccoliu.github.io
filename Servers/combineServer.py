'''This file is the server for the Code Assistance project. It is responsible for processing the code received from the frontend and returning the processed result to the frontend.'''

# Import necessary libraries
from openai import OpenAI  # OpenAI API
from flask import Flask, request, jsonify  # Flask interface
from flask_cors import CORS

import ssl  # Local https key
from bson import json_util  # For MongoDB may use the json_util

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
INTERPRETER = 'You are a master of sentence comprehension. When you receive language in various forms, you organize its requests into a bulleted list. For example: "I want a program that can perform addition and subtraction and output the result to the screen." Response: 1. Addition and subtraction functionality 2. Output the result to the screen.'

CODE_GENERATER = "You are a program generator that produces programs based on bulleted lists of requirements.Use the language:"

ANALYST = "You are a program issue analyst, adept at identifying potential problems by observing code. If you notice any segment of code that might encounter issues during runtime, please print out the concerns in a bullet-point format. If you find no issues, simply print out the phrase 'No issues'."

CODE_MASTER = "You are a coding master, skilled at helping others modify their source code to ensure it runs correctly. If you receive only the source code, you will directly make corrections. If you receive both the source code and a list of potential issues, you will compare each item against the source code and analyze whether these issues may occur. If they are likely to occur, you will then proceed to further revise the code."

REVERSE_DISCRIBER = "You are a reverse engineer, capable of understanding the source code and discribing its' functionality or what this code is doing in sentences."

BLUESKY_THINKER = "You are full of imagination, you will read the input from user and extend the feature, to make more functionality or better function, and you will output it in desciption. For example, if a user says 'Give me a maze game' you might respond with, 'A maze game where the user can walk around the maze, possibly encounter monsters, and the player can find treasures......'."

COMPELETION_CHECKER = "When you receive a source code, you read the comment in the code and if the comment part doesn't implement, you will fill the function and return the compelete source code."

SIMILARITY_CHECKER = "You are a similarity checker, you will compare the original code and the modified code(if exists), and return the similarity between them, If only one code is provided, you need to check whether the code is made by AI or human."

# Deine some phrases for the server to use.

ASK_FOR_CODE = "Give me the compelete source code after you have modify or generate it, if there is no changes at all, just return the original source code, there is no need to explain what you have done, just return the code."

ASK_FOR_LIST = "Please give me in a bulleted list."

ASK_FOR_COMPELETION = "Please give me the compelete source code."

SIMILARITY_FORMAT = "If there exists two codes, please analyze the percentage of similarity between them. The legal output format should be: \"The similarity between the two codes is: (Percentage Input) \", with analysis in the following newlines. For the last paragraph, judge if the code is plagiarized between the two codes or not, you can infer by the percentage and the analysis."


# This function will transfer user's request into bulleted list.
def analyzeInputSentence(inputSentence):
    analyzeInput = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": INTERPRETER,
            },
            {
                "role": "user",
                "content": inputSentence,
            },
        ],
    )
    # Print the bulleted list of the user's request use for debugging.
    print("This is the bulleted list of the user's request: \n")
    print(analyzeInput.choices[0].message.content)

    return analyzeInput.choices[0].message.content


# This function will generate code according to the bullet list
def generateCode(requirement, lang):
    generateResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": CODE_GENERATER + lang,
            },
            {
                "role": "user",
                "content": requirement + "\n" + ASK_FOR_CODE,
            },
        ],
    )
    # Print the code gpt generated, use for debugging.
    print("This is the generated code: \n")
    print(generateResult.choices[0].message.content)

    return generateResult.choices[0].message.content


# This function will read the source code and return a list of potential problems.
def analyzeCode(inputCode):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": ANALYST,
            },
            {
                "role": "user",
                "content": inputCode,
            },
        ],
    )
    # Print the problem list, use for debugging.
    print("This is the problem list: \n")
    print(analyzeResult.choices[0].message.content)

    return analyzeResult.choices[0].message.content


# This function wiil optimize the code using the source code and the problem list.
def optimizeCode(inputCode, problemList):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": CODE_MASTER,
            },
            {
                "role": "user",
                "content": "Here is the source code\n"
                + inputCode
                + "\n"
                + "Here are the problems that may occur\n"
                + problemList
                + "\n"
                + ASK_FOR_CODE,
            },
        ],
    )
    print(analyzeResult.choices[0].message.content)
    return analyzeResult.choices[0].message.content


# This function will add extra features to the original input sentence.
def addFeature(inputSentence):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": BLUESKY_THINKER,
            },
            {
                "role": "user",
                "content": inputSentence,
            },
        ],
    )
    print(analyzeResult.choices[0].message.content)
    return analyzeResult.choices[0].message.content


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
    print(analyzeResult.choices[0].message.content)
    return analyzeResult.choices[0].message.content


def fillFunction(inputCode):
    analyzeResult = client_model_2.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": COMPELETION_CHECKER,
            },
            {
                "role": "user",
                "content": inputCode + "\n" + ASK_FOR_COMPELETION,
            },
        ],
    )
    print(analyzeResult.choices[0].message.content)
    return analyzeResult.choices[0].message.content


def getSimilarity(firstInputCode, secondInputCode):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": SIMILARITY_CHECKER,
            },
            {
                "role": "user",
                "content": "Here is the LHS code\n"
                + firstInputCode
                + "\n"
                + "Here is the RHS code\n"
                + secondInputCode
                + "\n"
                + SIMILARITY_FORMAT,
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
            "fineTune", "codoctopus", code, optimizedCode, summary
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
        moreFeature = addFeature(userInput)

        requirmentList = analyzeInputSentence(moreFeature)
        # Generate code in specific language
        genResult = generateCode(requirmentList, targetLanguage)

        final = fillFunction(genResult)

        summary = describeCode(final)

        dataId = dbTools.insertGenerateDocument(
            "fineTune", "codoctopus", userInput, lang, requirmentList, final, summary
        )

        print(final + "\n")

        output = f"{final}"
        # Return the processed result to the frontend
        return jsonify({"result": output, "id": str(dataId)})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/similarity", methods=["POST"])
def similarity():
    try:
        data = request.get_json()

        firstInput = data.get("code1", "")
        secondInput = data.get("code2", "")

        if secondInput != "":
            output = getSimilarity(firstInput, secondInput)

        return jsonify({"result": output})
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

        dbTools.updateDocument("fineTune", "codoctopus", id, "rate", rate)
        dbTools.updateDocument("fineTune", "codoctopus", id, "comment", comment)

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

        searchResult = [[]]
        searchResult = dbTools.communitySearch("fineTune", "codoctopus", data)

        # return list of searched arrays

        # Retuen two dimesional array to the frontend
        return json_util.dumps(searchResult)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/viewData", methods=["POST"])
def view():
    try:
        id = request.get_json()
        lang = None

        # Get the keyword from the frontend
        mode = dbTools.getMode("fineTune", "codoctopus", id)
        if mode == "modify code":
            origin = dbTools.getOriginMessage("fineTune", "codoctopus", id)
            output = dbTools.getGptOutput("fineTune", "codoctopus", id)
            summary = dbTools.getSummary("fineTune", "codoctopus", id)
        elif mode == "generate code":
            lang = dbTools.getLang("fineTune", "codoctopus", id)
            origin = dbTools.getOriginMessage("fineTune", "codoctopus", id)
            output = dbTools.getGptOutput("fineTune", "codoctopus", id)
            summary = dbTools.getSummary("fineTune", "codoctopus", id)

        if lang == None:
            lang = "undefined"

        return jsonify(
            {
                "id": str(id),
                "mode": mode,
                "lang": lang,
                "original": origin,
                "output": output,
                "summary": summary,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/viewer_comment", methods=["POST"])
def viewer_comment():
    try:
        data = request.get_json()

        rate = data.get("rate", "")
        comment = data.get("comment", "")
        id = data.get("id", "")

        dbTools.updateCommentToCommnity(id, rate, comment)

        return jsonify({"result": "success"})
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
