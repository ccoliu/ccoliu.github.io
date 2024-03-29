# server.py
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Read API keys from key file.
with open("key.txt", "r") as file:
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
interpreter = 'You are a master of sentence comprehension. When you receive language in various forms, you organize its requests into a bulleted list. For example: "I want a program that can perform addition and subtraction and output the result to the screen." Response: 1. Addition and subtraction functionality 2. Output the result to the screen.'
codeMaster = "You are a program generator that produces programs based on bulleted lists of requirements. If the list of requirements is incomplete, you will automatically fill in the essential functions and annotate them with comments. Use the language:"
styleChecker = "You are a coding style optimizer. You optimize the source code based on readability, reliability, and architectural aspects, without altering its functionality or output results. Please return the source code as is (including comments in the code). There's no need to separately list the reasons for changes or additional comments. If there is no need to improve, simply return the content that user enters."


# This function will transfer user's request into bulleted list
def analyzeUserInput(inputSentence):
    analyzeInput = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": interpreter,
            },
            {
                "role": "user",
                "content": inputSentence,
            },
        ],
    )
    return analyzeInput.choices[0].message.content


# This function will generate code according to the bullet list
def generateCode(requirement, lang):
    generateResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": codeMaster + lang,
            },
            {
                "role": "user",
                "content": requirement,
            },
        ],
    )
    return generateResult.choices[0].message.content


# This function will adjust the coding style into a better format
def adjustStyle(inputCode):
    adjustCodingStyle = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": styleChecker,
            },
            {
                "role": "user",
                "content": inputCode,
            },
        ],
    )
    return adjustCodingStyle.choices[0].message.content


# Port into generate code API
@app.route("/gen_code", methods=["POST"])
def gen_code():
    try:
        data = request.get_json()
        userInput = data.get("code", "")

        lang = data.get("lang", "")
        targetLanguage = f"{lang}"

        # Turn user input into list
        requirmentList = analyzeUserInput(userInput)
        # Generate code in specific language
        genResult = generateCode(requirmentList, targetLanguage)
        # Adjust coding style
        finalResult = adjustStyle(genResult)

        print(finalResult + "\n")

        output = f"{finalResult}"
        # Return the processed result to the frontend
        return jsonify({"result": output})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
