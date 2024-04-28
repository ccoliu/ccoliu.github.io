'''This file is the server for the Code Assistance project. It is responsible for processing the code received from the frontend and returning the processed result to the frontend.'''

# Import necessary libraries
from openai import OpenAI  # OpenAI API
from flask import Flask, request, jsonify  # Flask interface
from flask_cors import CORS

import ssl  # Local https key
from bson import json_util  # For MongoDB may use the json_util
import threading

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
ANALYST = "You are a program issue analyst, adept at identifying potential problems by observing code. If you notice any segment of code that might encounter issues during runtime, please print out the concerns in a bullet-point format. If you find no issues, simply print out the phrase 'No issues'."

CODE_MASTER = "You are a coding master, skilled at helping others modify their source code to ensure it runs correctly. If you receive only the source code, you will directly make corrections. If you receive both the source code and a list of potential issues, you will compare each item against the source code and analyze whether these issues may occur. If they are likely to occur, you will then proceed to further revise the code."

REVERSE_DISCRIBER = "You are a reverse engineer, capable of understanding the source code and discribing its' functionality or what this code is doing in sentences."

SIMILARITY_CHECKER = "You are a similarity checker, you will compare the original code and the modified code(if exists), and return the similarity between them, If only one code is provided, you need to check whether the code is made by AI or human."

AI_CODE_CHECKER = "You are a code analyzer, you will analyze how many percentage of the code is generated by AI, and how many percentage of the code is written by human, and return the percentage of AI code and human code."

# Deine some phrases for the server to use.

ASK_FOR_CODE = "Give me the compelete source code after you have modify or generate it, if there is no changes at all, just return the original source code, there is no need to explain what you have done, just return the code."

ASK_FOR_LIST = "Please give me in a bulleted list."

ASK_FOR_COMPELETION = "Please give me the compelete source code."

SIMILARITY_FORMAT = "If there exists two codes, please analyze the percentage of similarity between them. The legal output format should be: \"The similarity between the two codes is: (Percentage Input) \", with analysis in the following newlines. For the last paragraph, judge if the code is plagiarized between the two codes or not, you can infer by the percentage and the analysis."

AI_CODE_FORMAT = ''' Analyze result:
AI code percentage: (Percentage)
Human code percentage: (Percentage)
(The human part and the ai part should be 100 in total)
'''

AI_CODE_CHECK_LOGIC = "You will reviced two code one is written by AI and the other is written by human, you need to analyze the code and return the percentage of AI code in the human code."

ISSUE_ANALYZER = "You are a code analyzer, when you recieve a source code, you will analyze the code and return the main target of the code which means what job can the code do."


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


def aiCodeChecker(inputCode, aiCode):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": AI_CODE_CHECKER,
            },
            {
                "role": "user",
                "content": AI_CODE_CHECK_LOGIC
                + "\n"
                + "Here is the human code\n"
                + inputCode
                + "\n"
                + "Here is the AI code\n"
                + aiCode
                + "\n"
                + "Please return in the following format:\n"
                + AI_CODE_FORMAT,
            },
        ],
    )

    print(analyzeResult.choices[0].message.content)
    return analyzeResult.choices[0].message.content


def getIssue(inputCode):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": ISSUE_ANALYZER,
            },
            {
                "role": "user",
                "content": "Here is the source code\n"
                + inputCode
                + "\n"
                + "Please return the main target of the code and the language source code uses.",
            },
        ],
    )

    # print(analyzeResult.choices[0].message.content)

    return analyzeResult.choices[0].message.content


def aiWriteCode(inputTarget):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a code master, good at writing code",
            },
            {
                "role": "user",
                "content": "Here is the main target\n"
                + inputTarget
                + "\n"
                + "Please help me write the code using the language in the main target.",
            },
        ],
    )

    # print(analyzeResult.choices[0].message.content)

    return analyzeResult.choices[0].message.content


# Display the server's web page use for debugging.
@app.route("/", methods=["GET"])
def index():
    helloWorld = "Welcome! This is the Code Assistance's Modify Server!"
    return helloWorld


def process_individual_code(code, results, index):
    try:
        problems = analyzeCode(code)
        optimizedCode = optimizeCode(code, problems)
        summary = describeCode(optimizedCode)

        dataId = dbTools.insertModifyDocument(
            "fineTune", "codoctopus", code, optimizedCode, summary
        )

        # Store result in the results list at the index corresponding to the original code
        results[index] = {"optimizedCode": optimizedCode, "summary": summary, "id": str(dataId)}
    except Exception as e:
        results[index] = {"error": str(e)}


# Process the code received from the frontend.
# Use for modify mode.
@app.route("/process_code", methods=["POST"])
def process_code():
    try:
        data = request.get_json()
        inputCode = data.get('longcode', [])

        threads = []
        results = [{} for _ in inputCode]  # Pre-allocate a list for results

        for index, code in enumerate(inputCode):
            thread = threading.Thread(target=process_individual_code, args=(code, results, index))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print(results)
        # Return the processed results to the frontend
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/similarity", methods=["POST"])
def similarity():
    try:
        # Get the data string from the frontend
        data = request.get_json()
        # Get the specifec item from the data string
        firstInput = data.get("code1", "")
        secondInput = data.get("code2", "")

        # If there are two input codes, compare them
        if secondInput != "":
            analyzeResult = getSimilarity(firstInput, secondInput)
            dbTools.insertsimilarityCheck(
                "fineTune", "similarityCheck", firstInput, secondInput, analyzeResult
            )
        else:
            issue = getIssue(firstInput)
            aiCode = aiWriteCode(issue)
            analyzeResult = aiCodeChecker(firstInput, aiCode)
            dbTools.insertsimilarityCheck(
                "fineTune", "similarityCheck", firstInput, aiCode, analyzeResult
            )

        return jsonify({"result": analyzeResult})
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
