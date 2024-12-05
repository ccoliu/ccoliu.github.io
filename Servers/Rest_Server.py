# ---------------------------------------------------
# Author:Daniel Hsiao (Github: https://github.com/whps970083),  ccoliu (Github: https://github.com/ccoliu)
# Date: 2024/10/01
# Update: 2024/12/05
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
import yaml  # Import the PyYAML library

# ---------------------------------------------------
'''Import the self-defined tools and functions'''
# ---------------------------------------------------

import FormatEnforcer
from dataBase import dataBaseTools
from PlagiarismChecker import PlagiarismChecker

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


# Load the YAML file
def load_yaml_config(file_path):
    """Load configuration from a YAML file."""
    with open(file_path, "r") as yaml_file:
        return yaml.safe_load(yaml_file)


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
message_enforcer = FormatEnforcer.Enforcer()
similarity_helper = PlagiarismChecker()

# ---------------------------------------------------
'''Define the server and API keys'''
# ---------------------------------------------------

# Set up SSL key for Flask to use https.
cert_path = resource_path('certificate.crt')
key_path = resource_path('private_key.key')

# Set the server type to https or http
SERVER_TYPE = "https"
# Set the default GPT model to use
gpt_model = "gpt-3.5-turbo"

# Get current file path
# current_path = os.path.dirname(os.path.realpath(__file__))

# Load the configuration from the YAML file
config_file_path = resource_path("Servers\\Config.yaml")
config = load_yaml_config(config_file_path)

# Extract server configuration from the loaded YAML
SERVER_TYPE = config["ServerSettings"]["ConnectionType"]
gpt_model = config["ServerSettings"]["GptModel"]

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

# Get system roles from the configuration file
code_analyst = config["Roles"]["ANALYST"]
code_master = config["Roles"]["CODE_MASTER"]
reverse_discriber = config["Roles"]["REVERSE_DESCRIBER"]
similarity_checker_peer = config["Roles"]["SIMILARITY_CHECKER"]
similarity_checker_ai = config["Roles"]["AI_CHECKER"]
code_modifier = config["Roles"]["DEPENDENT_CODE_MODIFIER"]

# Get the system instructions from the configuration file
format_modified_code = config["Formats"]["ASK_FOR_CODE"]
format_similarity_peer = config["Formats"]["COPY_FROM_PEER_FORMAT"]
format_similarity_ai = config["Formats"]["COPY_FROM_AI_FORMAT"]
format_problem_list = config["Formats"]["PROBLEM_BULLET_LIST_FORMAT"]

# Similarity check instructions
judgement_accordance = config["Judgements"]["ACCORDANCE"]
judgement_accordance_ai = config["Judgements"]["ACCORDANCE_AI"]


# This function will read the source code and return a list of potential problems.
def analyze_user_code(input_code):

    gpt_output = client_model_1.chat.completions.create(
        model=gpt_model,
        messages=[
            {
                "role": "system",
                "content": code_analyst,
            },
            {
                "role": "user",
                "content": "Here is the user's source code\n"
                + input_code
                + "Please help me find the potential problems in the code and return in the following format:\n"
                + format_problem_list,
            },
        ],
    )

    return gpt_output.choices[0].message.content


# This function wiil optimize the code using the source code and the problem list.
def optimize_code(inputCode, problemList):

    gpt_output = client_model_1.chat.completions.create(
        model=gpt_model,
        messages=[
            {
                "role": "system",
                "content": code_master,
            },
            {
                "role": "user",
                "content": "Here is the source code\n"
                + inputCode
                + "\n"
                + "Here are the problems that may occur\n"
                + problemList
                + "\n"
                + format_modified_code,
            },
        ],
    )

    return gpt_output.choices[0].message.content


# This function will describe the code in one sentence. Use for code summarization stored in the database.
def summarize_code_in_sentence(inputCode):

    gpt_output = client_model_1.chat.completions.create(
        model=gpt_model,
        messages=[
            {
                "role": "system",
                "content": reverse_discriber,
            },
            {
                "role": "user",
                "content": inputCode
                + "\n"
                + "Please summarize what the code is doing in one sentence.(within 100 tokens)",
            },
        ],
        max_tokens=100,
    )

    return gpt_output.choices[0].message.content


def copy_from_peer_check(lhs_code, rhs_code):

    # Calculate the Levenshtein similarity score between the two codes
    lev_score = similarity_helper.compare_levenshtein(lhs_code, rhs_code)

    gpt_output = client_model_1.chat.completions.create(
        model=gpt_model,
        messages=[
            {
                "role": "system",
                "content": similarity_checker_peer,
            },
            {
                "role": "user",
                "content": (
                    "Here is the first code (LHS):\n"
                    + lhs_code
                    + "\n"
                    + "Here is the second code (RHS):\n"
                    + rhs_code
                    + "\n"
                    "Here is the Levenshtein similarity score between the two codes:\n"
                    + lev_score
                    + "\n"
                    + judgement_accordance
                    + "\n"
                    + "Return the result in the following format:\n"
                    f"{format_similarity_peer}"
                ),
            },
        ],
    )

    return gpt_output.choices[0].message.content


def copy_from_ai_check(input_code):

    gpt_output = client_model_1.chat.completions.create(
        model=gpt_model,
        messages=[
            {
                "role": "system",
                "content": similarity_checker_ai,
            },
            {
                "role": "user",
                "content": (
                    "You are an AI code similarity checker.\n\n"
                    "Here is the source code:\n"
                    f"{input_code}\n\n" + judgement_accordance_ai + "\n"
                    "Finally, return your analysis in the following format:\n"
                    f"{format_similarity_ai}"
                ),
            },
        ],
    )

    return gpt_output.choices[0].message.content


# This function will ask AI for writing code based on the input code.
def ai_write_code(inputCode):

    gpt_output = client_model_1.chat.completions.create(
        model=gpt_model,
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
                + "Modify the code into the structure and the coding style that you like.\n"
                + "Simply return the code that you have written, there is no need to explain what you have done, just return the code.\n",
            },
        ],
    )

    return gpt_output.choices[0].message.content


def modify_consider_dependency(inputString):

    gpt_output = client_model_1.chat.completions.create(
        model=gpt_model,
        messages=[
            {
                "role": "system",
                "content": code_modifier,
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

    return gpt_output.choices[0].message.content


def dependency_array_to_str(dependent_array):
    formatted_string = ""
    for index, content in enumerate(dependent_array):
        formatted_string += f"Tab {index + 1}: {content}\n"
    return formatted_string


def convert_to_final_output(inputString):
    lines = inputString.split('\n')
    content = []
    for line in lines:
        parts = line.split(':')
        if len(parts) > 1:
            content.append(parts[1].strip())

    return content


def replace_results_content(results, dependentArray, default_string="Can't identify the code."):
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


# ---------------------------------------------------
'''Define the API endpoints'''
# ---------------------------------------------------


@app.route("/", methods=["GET"])
def index():
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return "No referrer found, this is the default page."


# Modify the code received from the frontend different tab and execute in differnet thread.
def execute_each_tab_content(input_code, results_array, current_index, dependency_array):
    try:
        # Analyze the code and get the problem list
        code_problems = analyze_user_code(input_code)
        # Optimize the code based on the problem list
        fixed_code = optimize_code(input_code, code_problems)
        # Summarize the code in one sentence
        code_summary = summarize_code_in_sentence(fixed_code)

        # Store the modified code and summary in the database
        data_id = database_tools.insertModifyDocument(
            "fineTune", "codoctopus", input_code, fixed_code, code_summary
        )

        # Store the result in the results list
        results_array[current_index] = {
            "optimizedCode": fixed_code,
            "summary": code_summary,
            "id": str(data_id),
        }

        dependency_array.append(fixed_code)
    except Exception as e:
        results_array[current_index] = {"error": str(e)}


# Process the code received from the frontend.
# Use for modify mode.
@app.route("/process_code", methods=["POST"])
def process_code():
    try:
        data = request.get_json()
        input_code = data.get('longcode', [])

        # Create a list to store threads
        threads = []
        # Pre-allocate a list for results
        results_array = [{} for _ in input_code]
        # Pre-allocate a list for the modified code
        dependency_array = []

        for index, code in enumerate(input_code):
            thread = threading.Thread(
                target=execute_each_tab_content, args=(code, results_array, index, dependency_array)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Convert the dependency array to a long string
        afterDependencyCheck = dependency_array_to_str(dependency_array)
        # Modify the code based on the dependency
        afterDependencyCheck = modify_consider_dependency(afterDependencyCheck)
        # Convert the modified code to the final tab content
        afterDependencyCheck = convert_to_final_output(afterDependencyCheck)

        # Replace the results content with the modified code
        replace_results_content(afterDependencyCheck, results_array)

        # Return the processed results to the frontend
        return jsonify({"results": results_array})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/similarity", methods=["POST"])
def similarity():
    try:
        # Get the data string from the frontend
        data = request.get_json()
        # Get the specifec item from the data string
        lhs_input_code = data.get("code1", "")
        rhs_input_code = data.get("code2", "")

        # If there are two input codes, compare them
        if rhs_input_code != "":
            # MOD 20241204 Daniel enforce the format of the code
            analyzed_result = message_enforcer.strictlyFollowFormat(
                copy_from_peer_check,
                message_enforcer.is_valid_plagiarism_code_format,
                lhs_input_code,
                rhs_input_code,
            )

            database_tools.insertsimilarityCheck(
                "fineTune", "similarityCheck", lhs_input_code, rhs_input_code, analyzed_result
            )
        else:
            # MOD 20241204 Daniel enforce the format of the code
            ai_code = ai_write_code(lhs_input_code)

            # analyzeResult = aiCodeChecker(firstInput, aiCode)
            analyzed_result = message_enforcer.strictlyFollowFormat(
                copy_from_ai_check,
                message_enforcer.is_valid_ai_code_format,
                lhs_input_code,
            )

            database_tools.insertsimilarityCheck(
                "fineTune", "similarityCheck", lhs_input_code, ai_code, analyzed_result
            )

        # Output the result to the console and log file
        # print("Similarity check event:" + analyzeResult + "\n")

        return jsonify({"result": analyzed_result})
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


# ---------------------------------------------------
'''Run the server'''
# ---------------------------------------------------

if SERVER_TYPE == "http":
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
elif SERVER_TYPE == "https":
    if __name__ == "__main__":
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        app.run(host='0.0.0.0', port=61911, ssl_context=context)
