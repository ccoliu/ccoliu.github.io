# ---------------------------------------------------
# Codoctopus — Rest Blueprint
# Migrated from Servers/Rest_Server.py
# Routes: /process_code, /similarity, /retrieve_comment,
#         /communitySearch, /viewData, /viewer_comment
# ---------------------------------------------------

import threading
from flask import Blueprint, request, jsonify, current_app
from bson import json_util

from backend.extensions import (
    database_tools,
    document_builder,
    message_enforcer,
)
from backend.services.ai_service import (
    analyze_user_code,
    optimize_code,
    describe_code,
    copy_from_peer_check,
    copy_from_ai_check,
    modify_consider_dependency,
)

rest_bp = Blueprint("rest", __name__)


# ===================================================
# Helper functions
# ===================================================

def _get_db_config():
    db_config = current_app.config["DATABASE_CONFIG"]
    return {
        "database_name": db_config["DatabaseStructure"]["db_name"],
        "modify_collection": db_config["DatabaseStructure"]["modify_mode"]["collection"],
        "similarity_collection": db_config["DatabaseStructure"]["similarity_mode"]["collection"],
        "plagiarism_collection": db_config["DatabaseStructure"]["plagiarism_ai_mode"]["collection"],
        "viewer_collection": db_config["DatabaseStructure"]["viewer_mode"]["collection"],
    }


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
    cfg = _get_db_config()
    if len(dependentArray) < len(results):
        print("Error: final_modified array does not have enough entries.")
        return

    for index, result in enumerate(results):
        if 'optimizedCode' in result:
            if index < len(dependentArray):
                result['optimizedCode'] = dependentArray[index]
                data_id = result['id']
                database_tools.update_document(
                    cfg["database_name"],
                    cfg["modify_collection"],
                    data_id,
                    "final_output",
                    result['optimizedCode'],
                )
        else:
            result = default_string


def execute_each_tab_content(input_code, results_array, current_index, dependency_array, user_name, cfg, yaml_config):
    try:
        code_problems = analyze_user_code(input_code, yaml_config)
        fixed_code = optimize_code(input_code, code_problems, yaml_config)
        code_summary = describe_code(fixed_code, yaml_config)

        insert_document = document_builder.modify_document(
            input_code, fixed_code, code_summary, creator=user_name
        )
        data_id = database_tools.insert_document(
            cfg["database_name"], cfg["modify_collection"], insert_document
        )

        viewer_document = document_builder.viewer_document(data_id, code_summary, creator=user_name)
        database_tools.insert_document(cfg["database_name"], cfg["viewer_collection"], viewer_document)

        results_array[current_index] = {
            "optimizedCode": fixed_code,
            "summary": code_summary,
            "id": str(data_id),
        }

        dependency_array.append(fixed_code)
    except Exception as e:
        results_array[current_index] = {"error": str(e)}


# ===================================================
# Routes
# ===================================================

@rest_bp.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Rest API is running."})


@rest_bp.route("/process_code", methods=["POST"])
def process_code():
    try:
        data = request.get_json()
        input_code = data.get('longcode', [])
        creater_name = data.get('username', "")

        threads = []
        results_array = [{} for _ in input_code]
        dependency_array = []

        cfg = _get_db_config()  # Extract config in main thread
        yaml_config = current_app.config["YAML_CONFIG"] # Extract YAML config
        for index, code in enumerate(input_code):
            thread = threading.Thread(
                target=execute_each_tab_content,
                args=(code, results_array, index, dependency_array, creater_name, cfg, yaml_config),
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        afterDependencyCheck = dependency_array_to_str(dependency_array)
        afterDependencyCheck = modify_consider_dependency(afterDependencyCheck, yaml_config)
        afterDependencyCheck = convert_to_final_output(afterDependencyCheck)

        replace_results_content(afterDependencyCheck, results_array)

        return jsonify({"results": results_array})
    except Exception as e:
        return jsonify({"error": str(e)})


@rest_bp.route("/similarity", methods=["POST"])
def similarity():
    cfg = _get_db_config()
    try:
        data = request.get_json()
        lhs_input_code = data.get("code1", "")
        rhs_input_code = data.get("code2", "")
        creator_name = data.get("username", "")

        if rhs_input_code != "":
            analyzed_result = message_enforcer.strictlyFollowFormat(
                copy_from_peer_check,
                message_enforcer.is_valid_plagiarism_code_format,
                lhs_input_code,
                rhs_input_code,
            )

            insert_doc = document_builder.similarity_check_document(
                lhs_input_code, rhs_input_code, analyzed_result, creator=creator_name
            )
            database_tools.insert_document(
                cfg["database_name"], cfg["similarity_collection"], insert_doc
            )
        else:
            analyzed_result = message_enforcer.strictlyFollowFormat(
                copy_from_ai_check,
                message_enforcer.is_valid_ai_code_format,
                lhs_input_code,
            )

            insert_doc = document_builder.plagiarism_ai_document(
                lhs_input_code, analyzed_result, creator=creator_name
            )
            database_tools.insert_document(
                cfg["database_name"], cfg["plagiarism_collection"], insert_doc
            )

        return jsonify({"result": analyzed_result})
    except Exception as e:
        return jsonify({"error": str(e)})


@rest_bp.route("/retrieve_comment", methods=["POST"])
def retrieve_code():
    cfg = _get_db_config()
    try:
        data = request.get_json()
        rate = data.get("rate", "")
        comment = data.get("comment", "")
        id = data.get("id", "")

        database_tools.update_document_in_database(cfg["database_name"], id, "rate", rate)
        database_tools.update_document_in_database(cfg["database_name"], id, "comment", comment)

        return jsonify({"result": "success"})
    except Exception as e:
        return jsonify({"error": str(e)})


@rest_bp.route("/communitySearch", methods=["POST"])
def search():
    cfg = _get_db_config()
    try:
        data = request.get_json()
        searchResult = database_tools.community_search(
            cfg["database_name"], cfg["viewer_collection"], data
        )
        return json_util.dumps(searchResult)
    except Exception as e:
        return jsonify({"error": str(e)})


@rest_bp.route("/viewData", methods=["POST"])
def view():
    cfg = _get_db_config()
    try:
        id = request.get_json()
        use_language = None

        mode = database_tools.find_field_by_id(cfg["database_name"], id, "mode")

        if mode == "modify_mode":
            user_input = database_tools.find_field_by_id(cfg["database_name"], id, "user_input")
            final_output = database_tools.find_field_by_id(cfg["database_name"], id, "final_output")
            summary = database_tools.find_field_by_id(cfg["database_name"], id, "summary")
        elif mode == "generate_mode":
            use_language = database_tools.find_field_by_id(cfg["database_name"], id, "language")
            user_input = database_tools.find_field_by_id(cfg["database_name"], id, "user_input")
            final_output = database_tools.find_field_by_id(cfg["database_name"], id, "final_output")
            summary = database_tools.find_field_by_id(cfg["database_name"], id, "summary")

        if use_language is None:
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


@rest_bp.route("/viewer_comment", methods=["POST"])
def viewer_comment():
    cfg = _get_db_config()
    try:
        data = request.get_json()
        rate = data.get("rate", "")
        comment = data.get("comment", "")
        id = data.get("id", "")

        database_tools.update_data_chain(
            cfg["database_name"], cfg["viewer_collection"], id, "viewer_rate", rate
        )
        database_tools.update_data_chain(
            cfg["database_name"], cfg["viewer_collection"], id, "viewer_comment", comment
        )

        return jsonify({"result": "success"})
    except Exception as e:
        return jsonify({"error": str(e)})
