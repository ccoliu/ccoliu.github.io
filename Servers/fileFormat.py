import json
import shutil


class StringToJsonl:
    def __init__(self):
        print("you may format now")

    def formatToJSONL(self, question, content):
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
        with open('Misc/fineTuneData.jsonl', 'a') as file:
            file.write(jsonl_string + '\n')
            print("Write success")

    def makeBackUp(self):

        source_file = 'Misc/fineTuneData.jsonl'
        backup_file = 'Misc/backUpData.jsonl'

        # Copy file
        shutil.copyfile(source_file, backup_file)

        print("Backup success!")

    def copyFromBackUp(self):

        source_file = 'Misc/fineTuneData.jsonl'
        backup_file = 'Misc/backUpData.jsonl'

        # Copy file
        shutil.copyfile(backup_file, source_file)

        print("Copy success!")

    def clearFile(self, fileName):
        # Open with write mode and close it immediately
        with open(fileName, 'w') as file:
            pass

        print("File has been cleared!")

    # Read txt file into jsonl format Q: A: must be a pair
    def read_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
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
        for q, a in zip(questions, answers):
            self.formatToJSONL(q, a)
        return questions, answers
