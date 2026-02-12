# ---------------------------------------------------
# Codoctopus — Generate Blueprint
# Migrated from Servers/Generate_Server.py
# Routes: /gen_code, /execute_steps, /stream
# ---------------------------------------------------

import time
import threading
from flask import Blueprint, request, jsonify, Response, current_app

from backend.extensions import (
    database_tools,
    document_builder,
    message_enforcer,
)
from backend.services.ai_service import (
    describe_code,
    create_worksheet,
    employee_work,
    refine_program_pool,
    classify_all_jobs,
    get_final_display,
    assign_gpt_roles,
)

generate_bp = Blueprint("generate", __name__)


# ===================================================
# Helper functions (from Generate_Server.py)
# ===================================================

def extract_worksheet_content(input_text, member_roles, member_messages, main_problem):
    lines = input_text.strip().split('\n')
    for line in lines:
        if line.startswith("Main problem:"):
            main_problem = line.split("Main problem:")[1].strip()
        elif line.startswith("Member role:"):
            member_roles.append(line.split("Member role:")[1].strip())
        elif line.startswith("Member message:"):
            member_messages.append(line.split("Member message:")[1].strip())
    return main_problem


def convert_job_to_front_format(inputJobArray):
    outputJobArray = []
    for s in inputJobArray:
        lower_case_message = s.casefold()
        if lower_case_message.startswith("help me"):
            replaced_message = s.replace("Help me", "Job:", 1)
            replaced_message = replaced_message.replace("HELP ME", "Job:", 1)
            replaced_message = replaced_message.replace("help me", "Job:", 1)
            outputJobArray.append(replaced_message)
        else:
            outputJobArray.append("Job: " + s)
    return outputJobArray


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


def assign_layers(jobGroup, jobArray):
    jobGroup = preprocess_group_string(jobGroup)
    jobArray_processed = preprocess_job_array(jobArray)

    groupStringLines = jobGroup.split('\n')
    layers = []

    for currentJob in jobArray_processed:
        for line in groupStringLines:
            if currentJob in line:
                layerNumber = line.split(':')[0].split()[-1]
                layers.append(int(layerNumber))
                break

    return layers


def preprocess_job_array(jobArray):
    newJobArray = []
    for job in jobArray:
        processedJob = job.replace(' ', '').lower()
        newJobArray.append(processedJob)
    return newJobArray


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
                newLines.append(f'{groupName.lower()}:{groupContent}')
            else:
                newLines.append(line)
    return '\n'.join(newLines)


# ===================================================
# Per-request state (using a simple dict keyed by thread ident)
# In production, consider using Flask sessions or a task queue.
# ===================================================

_generate_state = {
    "currentProgress": "",
    "progressBar_current": 0,
    "progressBar_total": 0,
    "main_problem": "",
    "language": "",
    "ai_gen_tasks": [],
}


def job_worker(mainTarget, role, job, inputProgress, barrier, state, yaml_config):
    state["currentProgress"] = employee_work(mainTarget, role, job, inputProgress, yaml_config)
    barrier.wait()


def start_processing(mainTarget, roles, jobArray, layerIndex, state, yaml_config):
    threads = []
    state["progressBar_total"] = len(jobArray) + 1
    state["progressBar_current"] = 0

    for layer in set(layerIndex):
        print(f'Processing jobs in layer {layer}')
        jobLayers = [job for job, layerNumber in enumerate(layerIndex, 1) if layerNumber == layer]
        print(f'Jobs in layer {layer}: {jobLayers}')

        for jobIndex in jobLayers:
            print(f"Job {jobIndex} content: {jobArray[jobIndex - 1]}")

        layer_barrier = threading.Barrier(len(jobLayers))

        for jobIndex in jobLayers:
            thread = threading.Thread(
                target=job_worker,
                args=(
                    mainTarget,
                    roles[jobIndex - 1],
                    jobArray[jobIndex - 1],
                    state["currentProgress"],
                    layer_barrier,
                    state,
                    yaml_config,
                ),
            )
            threads.append(thread)
            thread.start()

        state["progressBar_current"] += len(jobLayers)

        for thread in threads:
            thread.join()

    return state["currentProgress"]


# ===================================================
# Routes
# ===================================================

@generate_bp.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Generate API is running."})


@generate_bp.route("/gen_code", methods=["POST"])
def gen_code():
    try:
        data = request.get_json()
        userInput = data.get("code", "")
        lang = data.get("lang", "")

        _generate_state["language"] = lang

        roles = []
        dividedJobs = []

        workSheet = create_worksheet(userInput, lang)
        _generate_state["main_problem"] = extract_worksheet_content(
            workSheet, roles, dividedJobs, _generate_state["main_problem"]
        )
        _generate_state["main_problem"] += "Using the language: " + lang
        dividedJobs = convert_job_to_front_format(dividedJobs)

        _generate_state["ai_gen_tasks"] = dividedJobs
        return jsonify({"result": dividedJobs})
    except Exception as e:
        return jsonify({"error": str(e)})


@generate_bp.route("/execute_steps", methods=["POST"])
def execute_steps():
    cfg = current_app.config["DATABASE_CONFIG"]
    database_name = cfg["DatabaseStructure"]["db_name"]
    generate_collection = cfg["DatabaseStructure"]["generate_mode"]["collection"]
    viewer_collection = cfg["DatabaseStructure"]["viewer_mode"]["collection"]

    try:
        data = request.get_json()
        user_confirm_task = data.get('steps', [])
        creater_name = data.get('username', "")

        user_confirm_task = convert_job_to_back_format(user_confirm_task)
        newRoles = assign_gpt_roles(user_confirm_task)
        taskGroup = classify_all_jobs(user_confirm_task, _generate_state["main_problem"])
        jobLayers = assign_layers(taskGroup, user_confirm_task)

        yaml_config = current_app.config["YAML_CONFIG"]

        final_output = start_processing(
            _generate_state["main_problem"], newRoles, user_confirm_task, jobLayers, _generate_state, yaml_config
        )

        final_prog_pool = message_enforcer.extract_section_content(final_output, "Program pool")
        final_output = refine_program_pool(_generate_state["main_problem"], final_prog_pool, yaml_config)

        final_output = message_enforcer.strictlyFollowFormat(
            get_final_display,
            message_enforcer.is_valid_message_format,
            final_output,
            _generate_state["main_problem"],
            yaml_config,
        )

        _generate_state["progressBar_current"] += 1

        time.sleep(1)
        summary = describe_code(final_output, yaml_config)

        insert_doc = document_builder.generate_document(
            _generate_state["main_problem"],
            _generate_state["language"],
            _generate_state["ai_gen_tasks"],
            user_confirm_task,
            final_output,
            summary,
            creator=creater_name,
        )
        data_id = database_tools.insert_document(database_name, generate_collection, insert_doc)
        viewer_doc = document_builder.viewer_document(data_id, summary, creator=creater_name)
        database_tools.insert_document(database_name, viewer_collection, viewer_doc)

        return jsonify({"result": final_output, "id": str(data_id)})
    except Exception as e:
        return jsonify({"error": str(e)})


@generate_bp.route('/stream')
def stream():
    def event_stream():
        try:
            while (
                _generate_state["progressBar_current"] < _generate_state["progressBar_total"]
                or _generate_state["progressBar_total"] == 0
            ):
                progress_message = (
                    f"{_generate_state['progressBar_current']},"
                    f"{_generate_state['progressBar_total']}\n"
                )
                yield f"data: {progress_message}\n\n"
                time.sleep(2)

            total = _generate_state["progressBar_total"]
            progress_message = f"{total},{total}\n"
            yield f"data: {progress_message}\n\n"
            time.sleep(1.5)
            return
        except GeneratorExit:
            print("Client disconnected gracefully.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            _generate_state["progressBar_total"] = 0
            _generate_state["progressBar_current"] = 0

    return Response(event_stream(), content_type='text/event-stream')
