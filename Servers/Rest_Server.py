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
import yaml  # Import the PyYAML library
from LogHelper import initialize_logging  # For logging

# ---------------------------------------------------
'''Import the self-defined tools and functions'''
# ---------------------------------------------------

import FormatEnforcer
from PlagiarismChecker import PlagiarismChecker
from DataBase import MongoDBTools, DocumentBuilder

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


# Initialize the logging
log_handler = initialize_logging("Rest")


message_enforcer = FormatEnforcer.Enforcer()
similarity_helper = PlagiarismChecker()
database_tools = MongoDBTools()
document_builder = DocumentBuilder()
# ---------------------------------------------------
'''Define the server and API keys'''
# ---------------------------------------------------

# Set up SSL key for Flask to use https.
cert_path = resource_path("Keys\\server_certificate.crt")
key_path = resource_path("Keys\\server_private_key.key")

# Set the server type to https or http
server_type = "https"
# Set the default GPT model to use
gpt_model = "gpt-3.5-turbo"

# Get current file path
# current_path = os.path.dirname(os.path.realpath(__file__))

# Load the configuration from the YAML file
config_file_path = resource_path("Config\\Config.yaml")
config = load_yaml_config(config_file_path)
database_file_path = resource_path("Config\\DatabaseConfig.yaml")
database_config = load_yaml_config(database_file_path)

# Extract server configuration from the loaded YAML
server_type = config["ServerSettings"]["ConnectionType"]
gpt_model = config["ServerSettings"]["GptModel"]

# Extract database configuration from the loaded YAML
database_name = database_config["DatabaseStructure"]["db_name"]
modify_collection_name = database_config["DatabaseStructure"]["modify_mode"]["collection"]
similarity_collection_name = database_config["DatabaseStructure"]["similarity_mode"]["collection"]
plagiarism_collection_name = database_config["DatabaseStructure"]["plagiarism_ai_mode"][
    "collection"
]
viewer_collection_name = database_config["DatabaseStructure"]["viewer_mode"]["collection"]


# Create a Flask app
app = Flask(__name__)
CORS(app)

# Read API keys from key file.
key_file_path = resource_path("Keys\\openai_key.txt")
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


def call_gpt(model_name, gpt_roles, input_string, max_tokens=None):
    """
    General function to call GPT models with specified parameters.

    :param model_name: The GPT model to use (e.g., "gpt-3.5-turbo").
    :param gpt_roles: The role for the GPT assistant (e.g., system instructions or persona).
    :param input_string: The user's question or input content.
    :param max_tokens: Optional. The maximum number of tokens in the response. If None, no limit is applied.
    :return: The GPT model's response as a string.
    """
    try:
        # Prepare the base parameters
        params = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": gpt_roles},
                {"role": "user", "content": input_string},
            ],
        }

        # Add max_tokens only if it is specified
        if max_tokens is not None:
            params["max_tokens"] = max_tokens

        # Call the GPT API
        response = client_model_1.chat.completions.create(**params)

        # Return the content of the first choice
        return response.choices[0].message.content
    except Exception as e:
        return f"Error occurred while calling GPT: {str(e)}"


def analyze_user_code(input_code):
    """
    Analyzes the given source code and returns a list of potential problems.

    :param input_code: The source code provided by the user as a string.
    :return: A string containing the list of potential problems identified by GPT.
    """
    # Define the role for GPT
    gpt_role = code_analyst

    # Define the input message for GPT
    input_message = (
        "Here is the user's source code\n"
        + input_code
        + "Please help me find the potential problems in the code and return in the following format:\n"
        + format_problem_list
    )

    # Call the generalized GPT function
    return call_gpt(gpt_model, gpt_role, input_message)


def optimize_code(input_code, problem_list):
    """
    Optimizes the given source code based on the identified problem list.

    :param input_code: The source code provided by the user as a string.
    :param problem_list: The list of problems identified in the source code.
    :return: A string containing the optimized version of the source code.
    """
    # GPT role is predefined as 'code_master'
    gpt_role = code_master

    # Define the input message for GPT
    input_message = (
        "Here is the source code:\n"
        + input_code
        + "\nHere are the problems that may occur:\n"
        + problem_list
        + "\nPlease help optimize the code and return the modified version in the following format:\n"
        + format_modified_code
    )

    # Call the generalized GPT function
    return call_gpt(gpt_model, gpt_role, input_message)


def describe_code(input_code):
    """
    This function reads the input code and describes it in human language.

    :param inputCode: The source code to be analyzed and summarized.
    :return: A summarized description of the code in one sentence.
    """
    role = reverse_discriber
    input_sentence = input_code + "\n" + "Please summarize in 1 sentence within 100 tokens."
    max_tokens = 100

    # Call the generalized GPT function
    return call_gpt(gpt_model, role, input_sentence, max_tokens)


def copy_from_peer_check(lhs_code, rhs_code):
    """
    Checks for similarities between two pieces of code to identify potential copying.

    :param lhs_code: The first code snippet (LHS) as a string.
    :param rhs_code: The second code snippet (RHS) as a string.
    :return: A string containing the similarity analysis result.
    """
    # Calculate the Levenshtein similarity score between the two codes
    lev_score = similarity_helper.compare_levenshtein(lhs_code, rhs_code)

    # GPT role is predefined as 'similarity_checker_peer'
    gpt_role = similarity_checker_peer

    # Define the input message for GPT
    input_message = (
        "Here is the first code (LHS):\n"
        + lhs_code
        + "\nHere is the second code (RHS):\n"
        + rhs_code
        + "\nHere is the Levenshtein similarity score between the two codes:\n"
        + str(lev_score)
        + "\n"
        + judgement_accordance
        + "\nPlease return the result in the following format:\n"
        + format_similarity_peer
    )

    # Call the generalized GPT function
    return call_gpt(gpt_model, gpt_role, input_message)


def copy_from_ai_check(input_code):
    """
    Checks the input code for similarities with AI-generated patterns or known datasets.

    :param input_code: The source code to be analyzed.
    :return: A string containing the AI similarity analysis result.
    """
    # GPT role is predefined as 'similarity_checker_ai'
    gpt_role = similarity_checker_ai

    # Define the input message for GPT
    input_message = (
        "You are an AI code similarity checker.\n\n"
        "Here is the source code:\n"
        f"{input_code}\n\n"
        + judgement_accordance_ai
        + "\nFinally, return your analysis in the following format:\n"
        + format_similarity_ai
    )

    # Call the generalized GPT function
    return call_gpt(gpt_model, gpt_role, input_message)


def modify_consider_dependency(input_string):
    """
    Modifies the code in different tabs while considering dependencies between them.

    :param input_string: The content of different tabs of source code as a string.
    :return: A string with the modified or unmodified code in the same format.
    """
    # GPT role is predefined as 'code_modifier'
    gpt_role = code_modifier

    # Define the input message for GPT
    input_message = (
        "Here is the content of different tabs of source code:\n"
        + input_string
        + "\nIf you find any tabs that are dependent on each other, please modify the code based on the problems that may occur in the code. "
        + "If all the code is fine, don't change anything.\n"
        + "Please return in the exact same format you received (Tab #: content). "
        + "All tabs should be printed no matter if the content has been modified or not. (Do not explain what you have done.)\n"
    )

    # Call the generalized GPT function
    return call_gpt(gpt_model, gpt_role, input_message)


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

                data_id = result['id']
                field_name = "final_output"
                replace_content = result['optimizedCode']

                database_tools.update_document(
                    database_name, modify_collection_name, data_id, field_name, replace_content
                )
        else:
            result = default_string


# Modify the code received from the frontend different tab and execute in differnet thread.
def execute_each_tab_content(input_code, results_array, current_index, dependency_array):
    try:
        # Analyze the code and get the problem list
        code_problems = analyze_user_code(input_code)
        # Optimize the code based on the problem list
        fixed_code = optimize_code(input_code, code_problems)
        # Summarize the code in one sentence
        code_summary = describe_code(fixed_code)

        insert_document = document_builder.modify_document(input_code, fixed_code, code_summary)
        data_id = database_tools.insert_document(
            database_name, modify_collection_name, insert_document
        )

        viewer_document = document_builder.viewer_document(data_id, code_summary)
        database_tools.insert_document(database_name, viewer_collection_name, viewer_document)

        # Store the result in the results list
        results_array[current_index] = {
            "optimizedCode": fixed_code,
            "summary": code_summary,
            "id": str(data_id),
        }

        dependency_array.append(fixed_code)
    except Exception as e:
        results_array[current_index] = {"error": str(e)}


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

            # Insert the document into the database
            insert_document = document_builder.similarity_check_document(
                lhs_input_code, rhs_input_code, analyzed_result
            )
            database_tools.insert_document(
                database_name, similarity_collection_name, insert_document
            )

        else:
            # analyzeResult = aiCodeChecker(firstInput, aiCode)
            analyzed_result = message_enforcer.strictlyFollowFormat(
                copy_from_ai_check,
                message_enforcer.is_valid_ai_code_format,
                lhs_input_code,
            )

            insert_document = document_builder.plagiarism_ai_document(
                lhs_input_code, analyzed_result
            )
            database_tools.insert_document(
                database_name, plagiarism_collection_name, insert_document
            )

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

        database_tools.update_document_in_database(database_name, id, "rate", rate)
        database_tools.update_document_in_database(database_name, id, "comment", comment)

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

        searchResult = database_tools.community_search(database_name, viewer_collection_name, data)

        # Retuen two dimesional array to the frontend
        return json_util.dumps(searchResult)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/viewData", methods=["POST"])
def view():
    try:
        id = request.get_json()
        use_language = None

        mode = database_tools.find_field_by_id(database_name, id, "mode")

        if mode == "modify_mode":
            user_input = database_tools.find_field_by_id(database_name, id, "user_input")
            final_output = database_tools.find_field_by_id(database_name, id, "final_output")
            summary = database_tools.find_field_by_id(database_name, id, "summary")
        elif mode == "generate_mode":
            use_language = database_tools.find_field_by_id(database_name, id, "language")
            user_input = database_tools.find_field_by_id(database_name, id, "user_input")
            final_output = database_tools.find_field_by_id(database_name, id, "final_output")
            summary = database_tools.find_field_by_id(database_name, id, "summary")

        if use_language == None:
            use_language = "undefined"

        return jsonify(
            {
                "id": str(id),
                "mode": mode,
                "lang": use_language,
                "original": user_input,
                "output": final_output,
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

        database_tools.update_data_chain(
            database_name, viewer_collection_name, id, "viewer_rate", rate
        )
        database_tools.update_data_chain(
            database_name, viewer_collection_name, id, "viewer_comment", comment
        )

        return jsonify({"result": "success"})
    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------------------------------------------
'''Run the server'''
# ---------------------------------------------------

if server_type == "http":
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
elif server_type == "https":
    if __name__ == "__main__":
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        app.run(host='0.0.0.0', port=61911, ssl_context=context)
