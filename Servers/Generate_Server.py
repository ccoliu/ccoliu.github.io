# ---------------------------------------------------
# Author:Daniel Hsiao (Github: https://github.com/whps970083),  ccoliu (Github: https://github.com/ccoliu)
# Date: 2024/10/01
# Update: 2024/12/01
# Version: <V10.1.0.0>
# ---------------------------------------------------

# Import the necessary libraries
import os
import sys
from flask import Flask, request, jsonify, redirect, Response
from flask_cors import CORS
from openai import OpenAI
import os
import time
import threading
import ssl
import yaml
from LogHelper import initialize_logging  # For logging
import FormatEnforcer
from DataBase import MongoDBTools, DocumentBuilder

# ---------------------------------------------------
'''System initialization and configuration'''
# ---------------------------------------------------


# Function to get the file path after packaging
def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Initialize the logging system
log_handler = initialize_logging("Genreate")

# Initialize Tools
message_inforcer = FormatEnforcer.Enforcer()
database_tools = MongoDBTools()
document_builder = DocumentBuilder()

# Set the server type to https or http
server_type = "https"
# Set the default GPT model to use
gpt_model = "gpt-3.5-turbo"


# Load the YAML file
def load_yaml_config(file_path):
    """Load configuration from a YAML file."""
    with open(file_path, "r") as yaml_file:
        return yaml.safe_load(yaml_file)


# Load the configuration from the YAML file
config_file_path = resource_path("Config.yaml")
config = load_yaml_config(config_file_path)
database_file_path = resource_path("DatabaseConfig.yaml")
database_config = load_yaml_config(database_file_path)

# Extract server configuration from the loaded YAML
server_type = config["ServerSettings"]["ConnectionType"]
gpt_model = config["ServerSettings"]["GptModel"]
# Extract database configuration from the loaded YAML
database_name = database_config["DatabaseStructure"]["db_name"]
generate_collection_name = database_config["DatabaseStructure"]["generate_mode"]["collection"]
viewer_collection_name = database_config["DatabaseStructure"]["viewer_mode"]["collection"]

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

# Set up SSL key for Flask to use https.
cert_path = resource_path('certificate.crt')
key_path = resource_path('private_key.key')


# Create a Flask app
app = Flask(__name__)
CORS(app)

# ---------------------------------------------------
'''Define some necessary roles for the team members.'''
# ---------------------------------------------------

boss = config["Roles"]["BOSS"]
presenter = config["Roles"]["PRESENTER"]
reverse_discriber = config["Roles"]["REVERSE_DISCRIBER"]
job_classifier = config["Roles"]["JOB_CLASSIFIER"]
job_assigner = config["Roles"]["JOB_ASSIGNER"]
# ---------------------------------------------------
'''Define some output format below.'''
# ---------------------------------------------------

# Note the enforced format is done.
format_worksheet = config["Formats"]["WORKSHEET_FORMAT"]
format_message = config["Formats"]["MESSAGE_FORMAT"]
format_fronted_output = config["Formats"]["FRONTED_OUTPUT_FORMAT"]
format_group = config["Formats"]["GROUPED_FORMAT"]
format_token = config["Formats"]["FORMAT_TOKEN"]

# ---------------------------------------------------
'''Define some functions below.'''
# ---------------------------------------------------


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


def create_worksheet(request, language):
    """
    This function creates a worksheet for the team to solve the given problem.

    :param request: The main target or problem to be addressed.
    :param language: The language the team members will use.
    :return: A worksheet in the specified format.
    """
    gpt_role = boss
    input_sentence = (
        "Please strictly follow the format below to create a worksheet for the team to solve the problem.\n"
        + format_worksheet
        + "How many members are needed to complete this project, as well as the messages of each member, is up to you. "
        + "It is **required** that the output strictly follows the above format, and any deviations are unacceptable.\n"
        + "The main target (request) is:\n"
        + request
        + "\n"
        + "Please make sure all the team members are using the language: "
        + language
    )
    max_tokens = None  # No limit on tokens for this function

    # Call the generalized GPT function
    return call_gpt(gpt_model, gpt_role, input_sentence, max_tokens)


# Use for getting the specific content from the worksheet.
def extract_worksheet_content(input_text, member_roles, member_messages, main_problem):
    # Splitting the text into lines
    lines = input_text.strip().split('\n')

    # Initialize lists to hold the roles and messages
    for line in lines:
        if line.startswith("Main problem:"):
            main_problem = line.split("Main problem:")[1].strip()
        elif line.startswith("Member role:"):
            member_roles.append(line.split("Member role:")[1].strip())
        elif line.startswith("Member message:"):
            member_messages.append(line.split("Member message:")[1].strip())

    return main_problem


def employee_work(main_target, system_role, job_content, input_progress):
    """
    Main API for AI Engineer to perform a specific job in the project.

    :param main_target: The main target or goal of the project.
    :param system_role: The role of the system (instructions for GPT).
    :param job_content: The job content or task assigned to the AI.
    :param input_progress: The progress or context from the last member.
    :return: The final output after completing the job.
    """
    # Construct user input for the main job
    job_instruction = (
        "Here is the main target of the project\n"
        + main_target
        + "\nHere is the last member's progress for you to refer:\n"
        + input_progress
        + "\nHere is the job that you need to do:\n"
        + job_content
        + "\n"
        + format_token
        + format_message
    )

    # Call GPT for the main job
    ai_response = call_gpt(gpt_model, system_role, job_instruction)

    # Extract sections from the input and AI response
    current_program_pool = message_inforcer.extract_section_content(input_progress, "Program pool")
    current_job_output = message_inforcer.extract_section_content(ai_response, "Current job output")

    # Handle empty program pool
    if current_program_pool == "Warning: No content was found.":
        current_program_pool = ""

    # Combine the program pool and current job output
    combine_instruction = (
        "Help me combine the following two strings:\n"
        + current_program_pool
        + "\n"
        + current_job_output
        + "\nSimply combine them together without any adjustment."
    )
    combined_output = call_gpt(
        gpt_model,
        "Help me combine the content of two strings without any adjustment.",
        combine_instruction,
    )

    # Insert the combined output back into the response under "Program pool"
    final_output = message_inforcer.insert_section(ai_response, "Program pool", combined_output)

    return final_output


def refine_program_pool(main_target, program_pool):
    """
    Refine the program pool to ensure it meets the main target without duplicates.

    :param main_target: The main target or goal of the project.
    :param program_pool: The current state of the program pool.
    :return: The refined program pool as a string.
    """
    gpt_role = "You are responsible for tidying up the program pool. Ensure the source code meets the main target without any duplicate code."

    # Construct the instruction for tidying up the program pool
    instruction = (
        "Here is the main target of the project:\n"
        + main_target
        + "\nHere is the program pool that contains all the code that has been done:\n"
        + program_pool
        + "\nPlease tidy up the program pool to ensure it meets the main target and keep all the functions in the program pool."
        + "Only return the source code, don't add any extra information."
    )

    # Call GPT without named parameters
    ai_output = call_gpt(
        gpt_model,
        gpt_role,
        instruction,
    )

    return ai_output


def classify_all_jobs(job_array, main_target):
    """
    Analyze the job content and classify jobs into groups based on dependency.

    :param job_array: List of jobs to be classified.
    :param main_target: The main target or goal of the project.
    :return: Grouped job classifications as a string.
    """
    # Convert job array to string format
    job_string = f"JOBS: {str(job_array)}"

    gpt_role = job_classifier
    # Construct user input for the GPT classification
    classification_instruction = (
        "Here are the Jobs that need to be classified:\n"
        + job_string
        + "\nHere is the main target of the project:\n"
        + main_target
        + "\nAccording to the main target, please group the jobs into the same group if they can be executed at the same time. "
        + "The jobs that need to be executed in sequence shouldn't be in the same group, and the jobs that can be executed in parallel should be in the same group.\n"
        + "Each group now becomes a larger job, and there is a definite sequence among groups. For instance, in group 1, there are some printing functions, while in group 2, the task is to combine these printing functions. "
        + "In group 3, the task is to test the functions from group 2. This means that the contents of groups 1, 2, and 3 are interrelated with the contents of other groups.\n"
        + "The group number should be the legitimate order of execution.\n"
        + format_token
        + format_group
    )

    # Call GPT for job classification
    gpt_group_format = call_gpt(
        gpt_model,
        gpt_role,
        classification_instruction,
    )

    return gpt_group_format


def get_final_display(current_progress, main_target):
    """
    Format the final output for the frontend display.

    :param current_progress: The current progress or final result of the project.
    :param main_target: The main target or goal of the project.
    :return: The formatted output ready for frontend display.
    """
    # Construct user input for the final display
    display_instruction = (
        "Here is the main target\n"
        + main_target
        + "\nHere is the final result:\n"
        + current_progress
        + "\n"
        + format_token
        + format_fronted_output
    )

    # Call GPT for final output formatting
    final_output = call_gpt(
        gpt_model,
        presenter,
        display_instruction,
    )

    return final_output


# Convert the tasks to the format that can be displayed on the frontend 'Job: ...... '
def convert_job_to_front_format(inputJobArray):
    outputJobArray = []

    for s in inputJobArray:
        # Format the message to lowercase
        lower_case_message = s.casefold()

        if lower_case_message.startswith("help me"):
            # replace the "help me" with "Job:"
            replaced_message = s.replace("Help me", "Job:", 1)
            replaced_message = replaced_message.replace("HELP ME", "Job:", 1)
            replaced_message = replaced_message.replace("help me", "Job:", 1)
            outputJobArray.append(replaced_message)
        else:
            # If the output is not start with "help me", then add "Job:" to the beginning of the message.
            outputJobArray.append("Job: " + s)

    return outputJobArray


# Convert the tasks back to the format that can be read by gpt 'Help me ...... '
def convert_job_to_back_format(inputJobArray):
    outputJobArray = []

    for s in inputJobArray:
        lower_case_message = s.casefold()

        if lower_case_message.startswith("job:"):
            replaced_message = s.replace("Job:", "Help me", 1)
            replaced_message = replaced_message.replace("JOB:", "Help me", 1)
            replaced_message = replaced_message.replace("job:", "Help me", 1)
            outputJobArray.append(replaced_message)
        else:
            outputJobArray.append("Help me" + s)

    return outputJobArray


def assign_gpt_roles(job_array):
    """
    Assign GPT roles to team members based on the job content.

    :param job_array: List of job descriptions for which roles need to be assigned.
    :return: A list of roles assigned to each job.
    """
    gpt_roles = []
    system_role = job_assigner
    for job_content in job_array:
        # Construct the user input for role assignment
        role_instruction = (
            "Here is the job:\n"
            + job_content
            + "\n"
            + "Please use one sentence to describe the role for this person.\n"
            + "For example: You are a program tester, you will test the program and find out the problem and fix it.\n"
        )

        # Call GPT for role assignment
        current_job_role = call_gpt(
            gpt_model,
            system_role,
            role_instruction,
        )

        gpt_roles.append(current_job_role)

    return gpt_roles


# This function will create the layer array for the jobs.
def assign_layers(jobGroup, jobArray):
    # Preprocess the jobGroup
    jobGroup = preprocess_group_string(jobGroup)
    # Preprocess the jobArray
    jobArray = preprocess_job_array(jobArray)

    groupStringLines = jobGroup.split('\n')
    layers = []

    for currentJob in jobArray:
        for line in groupStringLines:
            if currentJob in line:
                layerNumber = line.split(':')[0].split()[-1]
                layers.append(int(layerNumber))
                break

    return layers


# This function will deal with the job array to make sure there is no space in the job content.
def preprocess_job_array(jobArray):
    newJobArray = []

    for job in jobArray:
        processedJob = job.replace(' ', '').lower()
        newJobArray.append(processedJob)

    return newJobArray


# This function will deal with the group string to make sure there is no space in it.
def preprocess_group_string(inputGroupString):
    lines = inputGroupString.strip().split('\n')

    newLines = []
    for line in lines:
        if line.strip() in ['GROUPS_START', 'GROUPS_END']:
            newLines.append(line)
        else:
            if ':' in line:
                groupName, groupContent = line.split(':', 1)
                groupContent = groupContent.replace('[', "['").replace(']', "']")
                groupContent = groupContent.replace("', '", "','")
                groupContent = groupContent.replace(' ', '').lower()

                # Don't change the group name.
                newLines.append(f'{groupName.lower()}:{groupContent}')
            else:
                newLines.append(line)

    finalString = '\n'.join(newLines)
    return finalString


# The job worker called by threads.
def job_worker(mainTarget, role, job, inputProgress, barrier):
    global currentProgress
    # Call the single engineer to do the job.
    currentProgress = employee_work(mainTarget, role, job, inputProgress)

    # Wait for all the threads to finish the job.
    barrier.wait()


# The main function to start the processing all of the jobs.
def start_processing(mainTarget, roles, jobArray, layerIndex):
    # The shared variable to store the current progress of the project.
    global currentProgress, progressBar_current, progressBar_total

    # The thread pool to store all the threads in this layer.
    threads = []
    progressBar_total = len(jobArray) + 1
    progressBar_current = 0

    # Set the layer index to the set to avoid the duplicate layer.
    for layer in set(layerIndex):
        # Output the current info's
        print(f'Processing jobs in layer {layer}')

        jobLayers = [job for job, layerNumber in enumerate(layerIndex, 1) if layerNumber == layer]

        # Output the current info's
        print(f'Jobs in layer {layer}: {jobLayers}')

        for jobIndex in jobLayers:
            print(f"Job {jobIndex} content: {jobArray[jobIndex - 1]}")

        # Build a Barrier object to synchronize the threads
        layer_barrier = threading.Barrier(len(jobLayers))

        for jobIndex in jobLayers:
            # Create the thread for each job.
            thread = threading.Thread(
                target=job_worker,
                args=(
                    mainTarget,
                    roles[jobIndex - 1],
                    jobArray[jobIndex - 1],
                    currentProgress,
                    layer_barrier,
                ),
            )

            threads.append(thread)
            thread.start()

        progressBar_current += len(jobLayers)

        for thread in threads:
            thread.join()

    # After all the task is done, the final output will be the current progress.
    return currentProgress


# Variables for progress bar
progressBar_current = 0
progressBar_total = 0
currentProgress = ""
main_problem = ""
language = ""


@app.route("/", methods=["GET"])
def index():
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return "Unblock generate mode successfully! Now you can reutrn to the previous page and start to generate the code."


# This route is for the frontend analysis the code and generate the worksheet for the team to solve the problem.
@app.route("/gen_code", methods=["POST"])
def gen_code():
    try:
        global main_problem, ai_gen_tasks, language
        data = request.get_json()
        userInput = data.get("code", "")
        lang = data.get("lang", "")

        language = lang

        roles = []
        dividedJobs = []

        workSheet = create_worksheet(userInput, lang)
        main_problem = extract_worksheet_content(workSheet, roles, dividedJobs, main_problem)
        main_problem += "Using the language: " + lang
        dividedJobs = convert_job_to_front_format(dividedJobs)

        ai_gen_tasks = dividedJobs
        return jsonify({"result": dividedJobs})
    except Exception as e:
        return jsonify({"error": str(e)})


# This route is for executing the steps that the team members have done.
@app.route("/execute_steps", methods=["POST"])
def execute_steps():
    try:
        global main_problem, currentProgress, progressBar_current, progressBar_total, language
        data = request.get_json()
        # Should deal with the arrays that send back.
        user_confirm_task = data.get('steps', [])
        newRoles = []

        user_confirm_task = convert_job_to_back_format(user_confirm_task)
        newRoles = assign_gpt_roles(user_confirm_task)
        taskGroup = classify_all_jobs(user_confirm_task, main_problem)
        jobLayers = []
        jobLayers = assign_layers(taskGroup, user_confirm_task)

        # Start the processing of the jobs.
        final_output = start_processing(main_problem, newRoles, user_confirm_task, jobLayers)

        # Get the Program pool first.
        final_prog_pool = message_inforcer.extract_section_content(final_output, "Program pool")
        final_output = refine_program_pool(main_problem, final_prog_pool)

        # Let AI to gerate the final output content.
        # Force the final output code to follow the format.
        final_output = message_inforcer.strictlyFollowFormat(
            get_final_display,
            message_inforcer.is_valid_message_format,
            final_output,
            main_problem,
        )

        # Finshed the progress bar.
        progressBar_current += 1

        time.sleep(1)
        summary = describe_code(final_output)

        # Insert the data into the database.
        insert_document = document_builder.generate_document(
            main_problem, language, ai_gen_tasks, user_confirm_task, final_output, summary
        )
        data_id = database_tools.insert_document(
            database_name, generate_collection_name, insert_document
        )
        viewer_document = document_builder.viewer_document(data_id, summary)
        database_tools.insert_document(database_name, viewer_collection_name, viewer_document)

        return jsonify({"result": final_output, "id": str(data_id)})
    except Exception as e:
        return jsonify({"error": str(e)})


# SSE Streaming route for the progress bar
@app.route('/stream')
def stream():
    def event_stream():
        # To get the global variable of cuurent progress and total progress.
        global progressBar_current, progressBar_total

        try:
            # Loop until the progress bar is full.
            while progressBar_current < progressBar_total or progressBar_total == 0:
                progress_message = f"{progressBar_current},{progressBar_total}\n"
                yield f"data: {progress_message}\n\n"
                # print('Progress:', progress_message)
                # Sleep for 2 seconds then continue the loop.
                time.sleep(2)

            # Since the last message won't be sent, we need to send the final message.
            progress_message = f"{progressBar_total},{progressBar_total}\n"
            yield f"data: {progress_message}\n\n"

            # Make sure the last message is send before the return.
            time.sleep(1.5)
            return
        except GeneratorExit:
            print("Client disconnected gracefully.")
        except Exception as e:
            print(f"An error occurred: {e}")

        # The progress bar is done, so we need to reset the progress bar.
        finally:
            progressBar_total = 0
            progressBar_current = 0

    return Response(event_stream(), content_type='text/event-stream')


# Switch the server connection type
if server_type == "http":
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5001)
elif server_type == "https":
    if __name__ == "__main__":
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        app.run(host='0.0.0.0', port=56494, ssl_context=context)
