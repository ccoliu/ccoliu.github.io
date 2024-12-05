# ---------------------------------------------------
# Author:Daniel Hsiao (Github: https://github.com/whps970083),  ccoliu (Github: https://github.com/ccoliu)
# Date: 2024/10/01
# Update: 2024/12/02
# Version: <V10.0.1.0>
# ---------------------------------------------------

# ---------------------------------------------------
'''Import the necessary libraries and modules'''
# ---------------------------------------------------
import os
import sys
from openai import OpenAI  # OpenAI API
from flask import Flask, request, jsonify, redirect  # Flask interface
from flask_cors import CORS
import ssl  # Local https key
from bson import json_util  # For MongoDB may use the json_util
import threading
import logging
from datetime import datetime
import configparser  # For reading the config file (ini file)

# ---------------------------------------------------
'''Import the self-defined tools and functions'''
# ---------------------------------------------------

import FormatEnforcer
from dataBase import dataBaseTools

# ---------------------------------------------------
'''System initialization and configuration'''
# ---------------------------------------------------


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Get the current path of the server
current_path = resource_path("")

# Create a Log folder if it does not exist
log_folder_path = os.path.abspath(current_path + "/Log")
if not os.path.exists(log_folder_path):
    os.makedirs(log_folder_path)  # Create the log folder
    print(f"Log folder created: {log_folder_path}")


# Dynamic log handler to switch log files daily
class DynamicLogHandler:
    def __init__(self, log_folder):
        self.log_folder = log_folder
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.setup_general_logger()
        self.setup_web_logger()

    def setup_general_logger(self):
        """Set up the logger for general stdout logs."""
        self.general_log_file = os.path.join(
            self.log_folder, f"{self.current_date}_rest_server_logs.log"
        )
        self.general_logger = logging.getLogger("general")
        self.general_logger.setLevel(logging.INFO)
        self.general_logger.handlers = []  # Clear previous handlers

        # File handler for logging to a file
        general_file_handler = logging.FileHandler(self.general_log_file, mode="a")
        general_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.general_logger.addHandler(general_file_handler)

        # Stream handler for logging to console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.general_logger.addHandler(console_handler)

    def setup_web_logger(self):
        """Set up the logger for werkzeug (web-related) logs."""
        self.web_log_file = os.path.join(
            self.log_folder, f"{self.current_date}_rest_server_web_logs.log"
        )
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.setLevel(logging.INFO)
        werkzeug_logger.handlers = []  # Clear previous handlers
        web_file_handler = logging.FileHandler(self.web_log_file, mode="a")
        web_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        werkzeug_logger.addHandler(web_file_handler)

    def check_date_and_rotate_logs(self):
        """Check the date and rotate log files if the date has changed."""
        new_date = datetime.now().strftime("%Y-%m-%d")
        if new_date != self.current_date:
            self.current_date = new_date
            self.setup_general_logger()
            self.setup_web_logger()


# Initialize the dynamic log handler
log_handler = DynamicLogHandler(log_folder_path)


# Custom stream handler to log only stdout to the general log file and console
class StreamToLogger:
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        if message.strip():
            log_handler.check_date_and_rotate_logs()  # Check and rotate logs if needed
            self.logger.info(message.strip())

    def flush(self):
        pass


# Redirect stdout to both console and general logger
sys.stdout = StreamToLogger(log_handler.general_logger)


# Initialize Tools
database_tools = dataBaseTools()
message_inforcer = FormatEnforcer.Enforcer()

# ---------------------------------------------------
'''Define the server and API keys'''
# ---------------------------------------------------

# Set up SSL key for Flask to use https.
cert_path = resource_path('certificate.crt')
key_path = resource_path('private_key.key')

# Set the server type to https or http
SERVER_TYPE = "https"
# Set the default GPT model to use
GPT_MODEL = "gpt-3.5-turbo"

# Get current file path
current_path = os.path.dirname(os.path.realpath(__file__))
# Get the ini file path
config_file_path = os.path.join(current_path, "Config.ini")
# Get the config tool to manage the config file
config_tool = configparser.ConfigParser()

# Check if the config file exists
if not os.path.exists(config_file_path):
    raise FileNotFoundError(f"Config file not found at: {config_file_path}")
else:
    config_tool.read(config_file_path)
    # Get the connection type from the config file
    SERVER_TYPE = config_tool["ServerSettings"]["ConnectionType"]
    GPT_MODEL = config_tool["ServerSettings"]["GptModel"]

# Create a Flask app
app = Flask(__name__)
CORS(app)

# Read API keys from key file.
key_file_path = resource_path("key.txt")
with open(key_file_path, "r") as file:
    keys = file.readlines()

api_key_model_1 = keys[0].strip()
api_key_model_2 = keys[1].strip()
api_key_model_3 = keys[2].strip()

# Assign API keys to different models.
client_model_1 = OpenAI(api_key=api_key_model_1)  # Gpt-3.5-turbo-A
client_model_2 = OpenAI(api_key=api_key_model_2)  # Gpt-3.5-turbo-B
client_model_3 = OpenAI(api_key=api_key_model_3)  # Fine-Tuning-Model

# ---------------------------------------------------
'''Define the system roles and instructions'''
# ---------------------------------------------------

# Define system roles and their instructions.
ANALYST = "You are a program issue analyst, adept at identifying potential problems by observing code. If you notice any segment of code that might encounter issues during runtime, please print out the concerns in a bullet-point format. If you find no issues, simply print out the phrase 'No issues'."

CODE_MASTER = "You are a coding master, skilled at helping others modify their source code to ensure it runs correctly. If you receive only the source code, you will directly make corrections. If you receive both the source code and a list of potential issues, you will compare each item against the source code and analyze whether these issues may occur. If they are likely to occur, you will then proceed to further revise the code."

REVERSE_DISCRIBER = "You are a reverse engineer, capable of understanding the source code and discribing its' functionality or what this code is doing in sentences."

SIMILARITY_CHECKER = "You are a similarity checker, you will compare the original code and the modified code(if exists), and return the similarity between them, If only one code is provided, you need to check whether the code is made by AI or human."

AI_CHECKER = "You will reviced two code one is written by AI and the other is written by human, you need to analyze the code to determine if the human code copied the AI."

DEPENDENT_CODE_MODIFIER = "You are a code modifier, you will modify the code based on the problems that may occur in the code, and return the modified code."

# Define some format for the AI to follow.
ASK_FOR_CODE = '''
Give me the compelete source code after you have modify or generate it, if there is no changes at all, just return the original source code, there is no need to explain what you have done, just return the code.\n
You should return in the following format:\n
Using language: 
(Language the program use)
Main program: 
(The program code)
Things that had been modified:
- (The things that had been modified)
- (The things that had been modified)
etc.
'''

# Two code comapre plagiarism format
COPY_FROM_PEER_FORMAT = '''
Probability of Plagiarism:\n 
(Percentage (%) that the LHS code copy from RHS code)
Analysis:\n
(With analysis in the following newlines.)
Final Judgement:\n 
(Plagiarism/Not Plagiarism)
Jugement Reason:\n 
(Reasons using bullet points)
'''

# AI plagiarism format
COPY_FROM_AI_FORMAT = '''
Probability of AI code:\n 
(Percentage (%) that the LHS code might copy from AI (RHS) code)
Analysis:\n
(With analysis in the following newlines.)
Final Judgement:\n 
(Plagiarism/Written by human)
Jugement Reason:\n 
(Reasons using bullet points)
'''

# Define the format for the problem list.
PROBLEM_BULLIT_LIST_FORMAT = '''
Problem 1: 
(......)
Problem 2:
(......)
Problem 3:
(......)
etc.
(If there is no problem, just return "No issues" without any other content.)
'''


# This function will read the source code and return a list of potential problems.
def analyzeCode(input_code):

    # Use the GPT-3.5-turbo-A model to analyze the code.
    analyzeResult = client_model_1.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": ANALYST,
            },
            {
                "role": "user",
                "content": "Here is the user's source code\n"
                + input_code
                + "Please help me find the potential problems in the code and return in the following format:\n"
                + PROBLEM_BULLIT_LIST_FORMAT,
            },
        ],
    )

    return analyzeResult.choices[0].message.content


# This function wiil optimize the code using the source code and the problem list.
def optimizeCode(inputCode, problemList):
    analyzeResult = client_model_1.chat.completions.create(
        model=GPT_MODEL,
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

    # print(analyzeResult.choices[0].message.content)

    return analyzeResult.choices[0].message.content


# This function will read the code and decribe it in human language.
def describeCode(inputCode):
    analyzeResult = client_model_1.chat.completions.create(
        model=GPT_MODEL,
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

    # print(analyzeResult.choices[0].message.content)

    return analyzeResult.choices[0].message.content


# This function is for similarity check between two codes.
def getSimilarity(firstInputCode, secondInputCode):
    analyzeResult = client_model_1.chat.completions.create(
        model=GPT_MODEL,
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
                + COPY_FROM_PEER_FORMAT,
            },
        ],
    )

    # print(analyzeResult.choices[0].message.content)

    return analyzeResult.choices[0].message.content


# This fucntion is for AI code checker.
def aiCodeChecker(input_code, ai_code):

    gpt_output = client_model_1.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": AI_CHECKER,
            },
            {
                "role": "user",
                "content": AI_CHECKER
                + "\n"
                + "Here is the human code\n"
                + input_code
                + "\n"
                + "Here is the AI code\n"
                + ai_code
                + "\n"
                + "Help me determine how similar human code and AI code are, based on the logic, sturcture, and coding style of the code.\n"
                + "For example if the two code have all the same functions but the varaible name is different, you should think the human code is copied from AI code, on the other hand, if the AI code is highly structered and looked more neat, you should think the human code is written by human because human written code is usually not that neat.\n"
                + "Please return in the following format:\n"
                + COPY_FROM_AI_FORMAT,
            },
        ],
    )

    return gpt_output.choices[0].message.content


# This function will ask AI for writing code based on the input code.
def aiWriteCode(inputCode):
    analyzeResult = client_model_1.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a code master, good at writing code.",
            },
            {
                "role": "user",
                "content": "Here is the source code\n"
                + inputCode
                + "\n"
                + "First you will analzye the source code and find out all the job the code can do, then you will write a code that can do the same job as the source code based on your own logic, coding style, and structure.\n"
                + "Simply return the code you write.",
            },
        ],
    )

    return analyzeResult.choices[0].message.content


def modifyDependency(inputString):
    modifiedString = client_model_1.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": DEPENDENT_CODE_MODIFIER,
            },
            {
                "role": "user",
                "content": "Here is the content of diffferent tabs of source code\n"
                + inputString
                + "\n"
                + "If you find any tabs that are depent on each other, please modify the code based on the problems that may occur in the code, if all the code are fine, don't change any thing.\n"
                + "Please return in the exact same format you got(Tab #: content), all the tab should be print no matter the content had been modified or not.(do not explain what you have done.)\n",
            },
        ],
    )

    return modifiedString.choices[0].message.content


# Display the server's web page use for debugging.
# @app.route("/", methods=["GET"])
# def index():
#     helloWorld = "Welcome! This is the Code Assistance's Modify Server!"
#     return helloWorld


@app.route("/", methods=["GET"])
def index():
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return "No referrer found, this is the default page."


def processEachTab(code, results, index, dependedArray):
    try:
        problems = analyzeCode(code)
        optimizedCode = optimizeCode(code, problems)
        summary = describeCode(optimizedCode)

        dataId = database_tools.insertModifyDocument(
            "fineTune", "codoctopus", code, optimizedCode, summary
        )

        # Store result in the results list at the index corresponding to the original code
        results[index] = {"optimizedCode": optimizedCode, "summary": summary, "id": str(dataId)}
        dependedArray.append(optimizedCode)
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
        dependedArray = []
        for index, code in enumerate(inputCode):
            thread = threading.Thread(
                target=processEachTab, args=(code, results, index, dependedArray)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Now the each modified result is in a big string.
        afterDependencyCheck = converDependentArrayToString(dependedArray)
        print("first check")
        print(afterDependencyCheck)
        afterDependencyCheck = modifyDependency(afterDependencyCheck)
        print("second check")
        print(afterDependencyCheck)
        afterDependencyCheck = converToFinalTabContent(afterDependencyCheck)
        print("third check")
        print(afterDependencyCheck)
        replaceOptimizedCode(afterDependencyCheck, results)

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
            # MOD 20241204 Daniel enforce the format of the code
            # analyzeResult = getSimilarity(firstInput, secondInput)
            analyzeResult = message_inforcer.strictlyFollowFormat(
                getSimilarity,
                message_inforcer.is_valid_plagiarism_code_format,
                firstInput,
                secondInput,
            )
            database_tools.insertsimilarityCheck(
                "fineTune", "similarityCheck", firstInput, secondInput, analyzeResult
            )
        else:
            # MOD 20241204 Daniel enforce the format of the code
            aiCode = aiWriteCode(firstInput)
            # analyzeResult = aiCodeChecker(firstInput, aiCode)
            analyzeResult = message_inforcer.strictlyFollowFormat(
                getSimilarity, message_inforcer.is_valid_ai_code_format, firstInput, aiCode
            )
            database_tools.insertsimilarityCheck(
                "fineTune", "similarityCheck", firstInput, aiCode, analyzeResult
            )

        # Output the result to the console and log file
        print("Similarity check event:" + analyzeResult + "\n")

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

        database_tools.updateDocument("fineTune", "codoctopus", id, "rate", rate)
        database_tools.updateDocument("fineTune", "codoctopus", id, "comment", comment)

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
        searchResult = database_tools.communitySearch("fineTune", "codoctopus", data)

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
        mode = database_tools.getMode("fineTune", "codoctopus", id)
        if mode == "modify code":
            origin = database_tools.getOriginMessage("fineTune", "codoctopus", id)
            output = database_tools.getGptOutput("fineTune", "codoctopus", id)
            summary = database_tools.getSummary("fineTune", "codoctopus", id)
        elif mode == "generate code":
            lang = database_tools.getLang("fineTune", "codoctopus", id)
            origin = database_tools.getOriginMessage("fineTune", "codoctopus", id)
            output = database_tools.getGptOutput("fineTune", "codoctopus", id)
            summary = database_tools.getSummary("fineTune", "codoctopus", id)

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

        database_tools.updateCommentToCommnity(id, rate, comment)

        return jsonify({"result": "success"})
    except Exception as e:
        return jsonify({"error": str(e)})


def converDependentArrayToString(dependent_array):
    formatted_string = ""
    for index, content in enumerate(dependent_array):
        formatted_string += f"Tab {index + 1}: {content}\n"
    return formatted_string


def converToFinalTabContent(inputString):
    lines = inputString.split('\n')
    content = []
    for line in lines:
        parts = line.split(':')
        if len(parts) > 1:
            content.append(parts[1].strip())

    return content


def replaceOptimizedCode(results, dependentArray, default_string="Can't identify the code."):
    if len(dependentArray) < len(results):
        print("Error: final_modified array does not have enough entries.")
        return

    for index, result in enumerate(results):
        if 'optimizedCode' in result:
            if index < len(dependentArray):
                result['optimizedCode'] = dependentArray[index]
                database_tools.updateDocument(
                    "fineTune", "codoctopus", result['id'], "optimizedCode", result['optimizedCode']
                )
        else:
            result = default_string


# Condtion to pick which server to use.
if SERVER_TYPE == "http":
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
elif SERVER_TYPE == "https":
    if __name__ == "__main__":
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        app.run(host='0.0.0.0', port=61911, ssl_context=context)
