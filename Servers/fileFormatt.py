import os
import sys
import json
import shutil


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class StringToJsonl:
    def __init__(self):
        print("You may use format tools now!")
        print("Current file is write into fineTuneData.jsonl & fact.jsonl")

    # If type is Q&A then question is the question (input) and content is the expecting answer
    # If type is factDescription then question is the original code and content is the comment
    def formatToJSONL(self, type, question, content):
        # If the data enter type is Q&A or factDescription then format it into JSONL
        if type == "Q&A":
            jsonl_data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a coding-style master good at formatting codes into one specific coding style.",
                    },
                    {"role": "user", "content": "Give me a perfect coding style example."},
                    {"role": "assistant", "content": "Taiwan."},
                ]
            }
            # put things in data stream
            jsonl_data["messages"][-2]["content"] = question
            jsonl_data["messages"][-1]["content"] = content

            jsonl_string = json.dumps(jsonl_data)

            # Keep Writing Data to JSONL
            file_path = resource_path('Misc/fineTuneData.jsonl')
            with open(file_path, 'a') as file:
                file.write(jsonl_string + '\n')
                print("Write success")

        elif type == "factDescription":
            jsonl_data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a coding-style master good at formatting codes into one specific coding style.",
                    },
                    {"role": "user", "content": "Give me a perfect coding style example."},
                    {"role": "assistant", "content": "Taiwan."},
                ]
            }
            # put things in data stream
            jsonl_data["messages"][-2]["content"] = "How do you think about this coding?" + question
            jsonl_data["messages"][-1]["content"] = content

            jsonl_string = json.dumps(jsonl_data)

            # Keep Writing Data to JSONL
            file_path = resource_path('Misc/fact.jsonl')
            with open(file_path, 'a') as file:
                file.write(jsonl_string + '\n')
                print("Write success")
        else:
            print("Invalid type please enter Q&A or factDescription.")
            return

    def createBackUp(self):
        source_file = resource_path('Misc/fineTuneData.jsonl')
        backup_file = resource_path('Misc/backUpData.jsonl')

        # Copy file
        shutil.copyfile(source_file, backup_file)

        print("Create backup success!")

    def cpyFromBackUp(self, current_file):
        current_file_path = resource_path(current_file)
        backup_file = resource_path('Misc/backUpData.jsonl')

        # Copy file from backup to current file
        shutil.copyfile(backup_file, current_file_path)

        print("Copy success!")

    def clearFile(self, fileName):
        file_path = resource_path(fileName)
        # Open with write mode and close it immediately
        with open(file_path, 'w') as file:
            pass

        print("File has been cleared!")

    # Read txt file into jsonl format Q: A: must be a pair
    def read_file(self, filename, enterMode):
        file_path = resource_path(filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        questions = []
        answers = []
        current_question = ""
        current_answer = ""
        reading_question = False

        for line in lines:
            line = line.strip()
            if line.startswith("Q:"):
                # Save previous answer
                if current_answer:
                    answers.append(current_answer.strip())
                    current_answer = ""
                reading_question = True
                continue
            elif line.startswith("A:"):
                # Save previous question
                if current_question:
                    questions.append(current_question.strip())
                    current_question = ""
                reading_question = False
                continue

            if reading_question:
                current_question += line + "\n"
            else:
                current_answer += line + "\n"

        # Append the last question and answer
        if current_question:
            questions.append(current_question.strip())
        if current_answer:
            answers.append(current_answer.strip())

        # Write into Jsonl file
        for Q, A in zip(questions, answers):
            self.formatToJSONL(enterMode, Q, A)

        return questions, answers

    # Write DB data to JSONL file use for fine-tuning.
    # In type factDesctiption systemOutput put the request and userComment put the answer.
    def write_to_file(self, dataType, systemOutput, userRate, userComment, filePath):
        file_path = resource_path(filePath)
        # If the data gets from DB is modify.
        if dataType == "modify code":
            jsonl_data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a coding master good at writing perfect code care about readibility, maintainability and reliability.",
                    },
                    {"role": "user", "content": systemOutput},
                    {
                        "role": "assistant",
                        "content": "This code is"
                        + userRate
                        + "\n"
                        + "I think the code "
                        + userComment,
                    },
                ]
            }

            jsonl_string = json.dumps(jsonl_data)

            # Keep Writing Data to JSONL
            with open(file_path, 'a') as file:
                file.write(jsonl_string + '\n')
                print("Write success")

        elif dataType == "generate code":
            jsonl_data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a coding master good at writing perfect code care about readibility, maintainability and reliability.",
                    },
                    {"role": "user", "content": systemOutput},
                    {
                        "role": "assistant",
                        "content": "This code is"
                        + userRate
                        + "\n"
                        + "I think the code "
                        + userComment,
                    },
                ]
            }

            jsonl_string = json.dumps(jsonl_data)

            # Keep Writing Data to JSONL
            with open(file_path, 'a') as file:
                file.write(jsonl_string + '\n')
                print("Write success")

        elif dataType == "factDescription":
            jsonl_data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a coding master good at writing perfect code care about readibility, maintainability and reliability.",
                    },
                    {"role": "user", "content": systemOutput},
                    {"role": "assistant", "content": userComment},
                ]
            }

            jsonl_string = json.dumps(jsonl_data)

            # Keep Writing Data to JSONL
            with open(file_path, 'a') as file:
                file.write(jsonl_string + '\n')
                print("Write success")
        else:
            print("Error type! Please enter modify code or generate code or factDescription.")
            return
