# ---------------------------------------------------
# Codoctopus — AI Service (Google Gemini)
# Consolidated AI calling logic for Rest and Generate.
# ---------------------------------------------------

from flask import current_app
from backend.extensions import gemini_client, message_enforcer


def _get_config(provided_config=None):
    """Helper to read YAML config from Flask app context or provided argument."""
    if provided_config:
        return provided_config
    return current_app.config["YAML_CONFIG"]


# ===================================================
# Core Gemini call
# ===================================================

def call_ai(system_role, input_string, max_tokens=None, model_name=None):
    """
    General function to call Gemini models using the new google-genai SDK.
    """
    try:
        # If model_name isn't passed, try to get it from current_app (main thread only)
        if not model_name:
            model_name = current_app.config["AI_MODEL"]

        prompt = f"{system_role}\n\n{input_string}"

        config_params = {}
        if max_tokens is not None:
            config_params["max_output_tokens"] = max_tokens

        response = gemini_client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config_params if config_params else None,
        )
        return response.text
    except Exception as e:
        return f"Error occurred while calling AI: {str(e)}"


# ===================================================
# Rest-server functions (Modify / Similarity)
# ===================================================

def analyze_user_code(input_code, yaml_config=None):
    """Analyzes source code and returns a list of potential problems."""
    config = _get_config(yaml_config)
    gpt_role = config["Roles"]["ANALYST"]
    format_problem_list = config["Formats"]["PROBLEM_BULLET_LIST_FORMAT"]

    input_message = (
        "Here is the user's source code\n"
        + input_code
        + "Please help me find the potential problems in the code and return in the following format:\n"
        + format_problem_list
    )

    # Need to pass model name if running in thread? 
    # Actually call_ai relies on current_app.config["AI_MODEL"].
    # We should also pass model_name to call_ai if we are in a thread.
    # For now, let's assume Config.py/extensions holds the model name or we retrieve it from yaml_config if stored there.
    # But AI_MODEL is top level config.
    # Let's update call_ai to accept model_name too.
    
    # Extract model name from config or use default
    model_name = config.get("ServerSettings", {}).get("AiModel") or "gemini-2.0-flash"
    
    return call_ai(gpt_role, input_message, model_name=model_name)


def optimize_code(input_code, problem_list, yaml_config=None):
    """Optimizes source code based on the identified problem list."""
    config = _get_config(yaml_config)
    gpt_role = config["Roles"]["CODE_MASTER"]
    format_modified_code = config["Formats"]["ASK_FOR_CODE"]

    input_message = (
        "Here is the source code:\n"
        + input_code
        + "\nHere are the problems that may occur:\n"
        + problem_list
        + "\nPlease help optimize the code and return the modified version in the following format:\n"
        + format_modified_code
    )

    model_name = config.get("ServerSettings", {}).get("AiModel")
    return call_ai(gpt_role, input_message, model_name=model_name)


def describe_code(input_code, yaml_config=None):
    """Reads code and describes it in human language (1 sentence, ≤100 tokens)."""
    config = _get_config(yaml_config)
    role = config["Roles"]["REVERSE_DESCRIBER"]
    input_sentence = input_code + "\n" + "Please summarize in 1 sentence within 100 tokens."
    model_name = config.get("ServerSettings", {}).get("AiModel")
    return call_ai(role, input_sentence, max_tokens=100, model_name=model_name)


def copy_from_peer_check(lhs_code, rhs_code, yaml_config=None):
    """Checks similarity between two code snippets for potential plagiarism."""
    from backend.extensions import similarity_helper

    config = _get_config(yaml_config)
    lev_score = similarity_helper.compare_levenshtein(lhs_code, rhs_code)
    gpt_role = config["Roles"]["SIMILARITY_CHECKER"]
    format_similarity_peer = config["Formats"]["COPY_FROM_PEER_FORMAT"]
    judgement_accordance = config["Judgements"]["ACCORDANCE"]

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

    model_name = config.get("ServerSettings", {}).get("AiModel")
    return call_ai(gpt_role, input_message, model_name=model_name)


def copy_from_ai_check(input_code, yaml_config=None):
    """Checks code for similarities with AI-generated patterns."""
    config = _get_config(yaml_config)
    gpt_role = config["Roles"]["AI_CHECKER"]
    format_similarity_ai = config["Formats"]["COPY_FROM_AI_FORMAT"]
    judgement_accordance_ai = config["Judgements"]["ACCORDANCE_AI"]

    input_message = (
        "You are an AI code similarity checker.\n\n"
        "Here is the source code:\n"
        f"{input_code}\n\n"
        + judgement_accordance_ai
        + "\nFinally, return your analysis in the following format:\n"
        + format_similarity_ai
    )

    model_name = config.get("ServerSettings", {}).get("AiModel")
    return call_ai(gpt_role, input_message, model_name=model_name)


def modify_consider_dependency(input_string, yaml_config=None):
    """Modifies code in different tabs while considering dependencies."""
    config = _get_config(yaml_config)
    gpt_role = config["Roles"]["DEPENDENT_CODE_MODIFIER"]

    input_message = (
        "Here is the content of different tabs of source code:\n"
        + input_string
        + "\nIf you find any tabs that are dependent on each other, please modify the code based on the problems that may occur in the code. "
        + "If all the code is fine, don't change anything.\n"
        + "Please return in the exact same format you received (Tab #: content). "
        + "All tabs should be printed no matter if the content has been modified or not. (Do not explain what you have done.)\n"
    )

    model_name = config.get("ServerSettings", {}).get("AiModel")
    return call_ai(gpt_role, input_message, model_name=model_name)


# ===================================================
# Generate-server functions
# ===================================================

def create_worksheet(request_text, language, yaml_config=None):
    """Creates a worksheet for the team to solve a given problem."""
    config = _get_config(yaml_config)
    gpt_role = config["Roles"]["BOSS"]
    format_worksheet = config["Formats"]["WORKSHEET_FORMAT"]

    input_sentence = (
        "Please strictly follow the format below to create a worksheet for the team to solve the problem.\n"
        + format_worksheet
        + "How many members are needed to complete this project, as well as the messages of each member, is up to you. "
        + "It is **required** that the output strictly follows the above format, and any deviations are unacceptable.\n"
        + "The main target (request) is:\n"
        + request_text
        + "\n"
        + "Please make sure all the team members are using the language: "
        + language
    )

    model_name = config.get("ServerSettings", {}).get("AiModel")
    return call_ai(gpt_role, input_sentence, model_name=model_name)


def employee_work(main_target, system_role, job_content, input_progress, yaml_config=None):
    """Main API for AI Engineer to perform a specific job."""
    config = _get_config(yaml_config)
    format_token = config["Formats"]["FORMAT_TOKEN"]
    format_message = config["Formats"]["MESSAGE_FORMAT"]

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

    model_name = config.get("ServerSettings", {}).get("AiModel")
    ai_response = call_ai(system_role, job_instruction, model_name=model_name)

    current_program_pool = message_enforcer.extract_section_content(input_progress, "Program pool")
    current_job_output = message_enforcer.extract_section_content(ai_response, "Current job output")

    if current_program_pool == "Warning: No content was found.":
        current_program_pool = ""

    combine_instruction = (
        "Help me combine the following two strings:\n"
        + current_program_pool
        + "\n"
        + current_job_output
        + "\nSimply combine them together without any adjustment."
    )
    combined_output = call_ai(
        "Help me combine the content of two strings without any adjustment.",
        combine_instruction,
        model_name=config.get("ServerSettings", {}).get("AiModel")
    )

    final_output = message_enforcer.insert_section(ai_response, "Program pool", combined_output)
    return final_output


def refine_program_pool(main_target, program_pool, yaml_config=None):
    """Refine the program pool to ensure it meets the main target."""
    config = _get_config(yaml_config)
    
    gpt_role = (
        "You are responsible for tidying up the program pool. "
        "Ensure the source code meets the main target without any duplicate code."
    )

    instruction = (
        "Here is the main target of the project:\n"
        + main_target
        + "\nHere is the program pool that contains all the code that has been done:\n"
        + program_pool
        + "\nPlease tidy up the program pool to ensure it meets the main target and keep all the functions in the program pool."
        + "Only return the source code, don't add any extra information."
    )

    model_name = config.get("ServerSettings", {}).get("AiModel")
    return call_ai(gpt_role, instruction, model_name=model_name)


def classify_all_jobs(job_array, main_target, yaml_config=None):
    """Classify jobs into groups based on dependency."""
    config = _get_config(yaml_config)
    gpt_role = config["Roles"]["JOB_CLASSIFIER"]
    format_group = config["Formats"]["GROUPED_FORMAT"]
    format_token = config["Formats"]["FORMAT_TOKEN"]

    job_string = f"JOBS: {str(job_array)}"

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

    model_name = config.get("ServerSettings", {}).get("AiModel")
    return call_ai(gpt_role, classification_instruction, model_name=model_name)


def get_final_display(current_progress, main_target, yaml_config=None):
    """Format the final output for the frontend display."""
    config = _get_config(yaml_config)
    presenter = config["Roles"]["PRESENTER"]
    format_fronted_output = config["Formats"]["FRONTED_OUTPUT_FORMAT"]
    format_token = config["Formats"]["FORMAT_TOKEN"]

    display_instruction = (
        "Here is the main target\n"
        + main_target
        + "\nHere is the final result:\n"
        + current_progress
        + "\n"
        + format_token
        + format_fronted_output
    )

    model_name = config.get("ServerSettings", {}).get("AiModel")
    return call_ai(presenter, display_instruction, model_name=model_name)


def assign_gpt_roles(job_array, yaml_config=None):
    """Assign AI roles to team members based on the job content."""
    config = _get_config(yaml_config)
    system_role = config["Roles"]["JOB_ASSIGNER"]
    gpt_roles = []

    for job_content in job_array:
        role_instruction = (
            "Here is the job:\n"
            + job_content
            + "\n"
            + "Please use one sentence to describe the role for this person.\n"
            + "For example: You are a program tester, you will test the program and find out the problem and fix it.\n"
        )

        model_name = config.get("ServerSettings", {}).get("AiModel")
        current_job_role = call_ai(system_role, role_instruction, model_name=model_name)
        gpt_roles.append(current_job_role)

    return gpt_roles
