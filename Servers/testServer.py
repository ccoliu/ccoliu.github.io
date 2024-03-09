# server.py
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS
import ssl  # for local https key


app = Flask(__name__)
CORS(app)

# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()

api_key_model_1 = keys[0].strip()
api_key_model_2 = keys[1].strip()

# Assign API keys to different models.
client_model_1 = OpenAI(api_key=api_key_model_1)  # For gpt-3.5-turbo-A
client_model_2 = OpenAI(api_key=api_key_model_2)  # For gpt-3.5-turbo-B

# Set up SSL key for Flask to use https.
cert_path = 'C:/Users/whps9/ccoliu.github.io/certificate.crt'
key_path = 'C:/Users/whps9/ccoliu.github.io/private_key.key'


# Check if the server is running.
@app.route("/", methods=["GET"])
def index():
    return "Hello, this is the code assistance server home page!"


# Define system roles and their instructions.
analyst = "You are a program issue analyst, adept at identifying potential problems by observing code. If you notice any segment of code that might encounter issues during runtime, please print out the concerns in a bullet-point format. If you find no issues, simply print out the phrase 'No issues'."

codeMaster = "You are a master programmer capable of modifying others' code based on existing scripts and desired functionalities. You can transform their code to achieve the expected functions while ensuring complete correctness and execution without issues. If there are no specific functionalities expected, then you focus on correcting the accuracy of others' code to ensure it runs correctly."

styleChecker = "You are a king of coding style transformation, taking into account factors such as maintainability, readability, and reliability. For instance, if the original code lacks comments, you will add annotations to enhance its readability. You aim to refactor the code without altering its original functionality, and output both the code and its comments, without the need to explain the reasons for the changes."


# Process the code received from the frontend.
@app.route("/process_code", methods=["POST"])
def process_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        # Perform backend processing here, this is just an example, you can insert your processing logic
        result = f"{code}"

        completionB = client_model_2.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": codeMaster,
                },
                {
                    "role": "user",
                    "content": code,
                },
            ],
        )

        result = f"{completionB.choices[0].message.content}"

        completionC = client_model_1.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": analyst,
                },
                {
                    "role": "user",
                    "content": result,
                },
            ],
        )
        completionD = client_model_2.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": codeMaster,
                },
                {
                    "role": "user",
                    "content": "Here is the code and the list of problems that may exist\n"
                    + code
                    + result,
                },
            ],
        )
        result = f"{completionD.choices[0].message.content}"

        completionE = client_model_2.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": styleChecker,
                },
                {
                    "role": "user",
                    "content": result,
                },
            ],
        )

        result = f"{completionE.choices[0].message.content}"
        # Return the processed result to the frontend
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    app.run(host='0.0.0.0', port=5000, ssl_context=context)
