# server.py
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS

 
app = Flask(__name__)
CORS(app)

# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()

api_key_model_1 = keys[0].strip()
api_key_model_2 = keys[1].strip()
api_key_model_3 = keys[2].strip()

# Assign API keys to different models.
client_model_1 = OpenAI(api_key=api_key_model_1)  # Gpt-3.5-turbo-A
client_model_2 = OpenAI(api_key=api_key_model_2)  # Gpt-3.5-turbo-B
client_model_3 = OpenAI(api_key=api_key_model_3)  # Fine-Tuning-Model

# Display the server's web page.
@app.route("/", methods=["GET"])
def index():
    return "Hello! This is the Code Assistance's Server home page!"

# Define system roles and their instructions.
interpreter = "You are a master of sentence comprehension. When you receive language in various forms, you organize its requests into a bulleted list. For example: \"I want a program that can perform addition and subtraction and output the result to the screen.\" Response: 1. Addition and subtraction functionality 2. Output the result to the screen."

codeMaster = "You are a program generator that produces programs based on bulleted lists of requirements. If the list of requirements is incomplete, you will automatically fill in the essential functions and annotate them with comments."

styleChecker = "You are a coding style optimizer. You optimize the source code based on readability, reliability, and architectural aspects, without altering its functionality or output results. Please return the source code as is (including comments in the code). There's no need to separately list the reasons for changes or additional comments. If there is no need to improve, simply return the content that user enter."

def analyzeCode(inputSentence):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {
                    "role": "system",
                    "content": interpreter,
                },
                {
                    "role": "user",
                    "content": inputSentence,
                }
        ],
    )
    return analyzeResult.choices[0].message.content

def generateCode(requirement):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {
                    "role": "system",
                    "content": codeMaster ,
                },
                {
                    "role": "user",
                    "content": requirement,
                }
        ],
    )
    return analyzeResult.choices[0].message.content

def optimizeCode(inputCode, problemList=None):
    if problemList is None:
        # 只有 source code 的處理方式
        analyzeResult = client_model_2.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": codeMaster,
                },
                {
                    "role": "user",
                    "content": inputCode,
                }
            ],
        )
    else:
        # 有 source code 和問題列表的處理方式
        analyzeResult = client_model_1.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": codeMaster,
                },
                {
                    "role": "user",
                    "content": "Here is the source code\n" + inputCode + "Here are the problems that may occur\n" + problemList,
                }
            ],
        )
    return analyzeResult.choices[0].message.content


def adjustStyle(inputCode):
    analyzeResult = client_model_2.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {
                    "role": "system",
                    "content": styleChecker,
                },
                {
                    "role": "user",
                    "content": inputCode,
                }
        ],
    )
    return analyzeResult.choices[0].message.content

# Process the code received from the frontend.
@app.route("/process_code", methods=["POST"])
def process_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        result = f"{code}"  # Initialize the result.

        optimizedResult = analyzeCode(code)
        print ( optimizedResult + "\n")
        
        result = f"{optimizedResult}"
        # Return the processed result to the frontend
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/gen_code", methods=["POST"])
def gen_code():
    try:
        data = request.get_json()
        code = data.get("code", "")
        
        lang = data.get("lang", "")
        target = f"{lang}"

        genList = generateCode(code,target)
        print ( genList + "\n")
        
        genresult = f"{genList}"
        # Return the processed result to the frontend
        return jsonify({"result": genresult})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)