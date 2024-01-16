# server.py
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS
import ssl  # Local https key

app = Flask(__name__)
CORS(app)

# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()

api_key_model_1 = keys[0].strip()
api_key_model_2 = keys[1].strip()

# Assign API keys to different models.
client_model_1 = OpenAI(api_key=api_key_model_1)  # Gpt-3.5-turbo-A
client_model_2 = OpenAI(api_key=api_key_model_2)  # Gpt-3.5-turbo-B

# Set up SSL key for Flask to use https.
cert_path = 'C:/Users/whps9/ccoliu.github.io/certificate.crt'
key_path = 'C:/Users/whps9/ccoliu.github.io/private_key.key'

# Display the server's web page.
@app.route("/", methods=["GET"])
def index():
    return "Hello! This is the code assistance server home page!"

# Define system roles and their instructions.
analyst = "You are a program issue analyst, adept at identifying potential problems by observing code. If you notice any segment of code that might encounter issues during runtime, please print out the concerns in a bullet-point format. If you find no issues, simply print out the phrase 'No issues'. If there exist issues, respond with a bullet-point list."

codeMaster = "You are a coding master, skilled at helping others modify their source code to ensure it runs correctly. If you receive only the source code, you will directly make corrections. If you receive both the source code and a list of potential issues, you will compare each item against the source code and analyze whether these issues may occur. If they are likely to occur, you will then proceed to further revise the code. You only need to return the source code and the comments."

styleChecker = "You are a coding style optimizer. You optimize the source code based on readability, reliability, and architectural aspects, without altering its functionality or output results. Please return the source code as is (including comments in the code). There's no need to separately list the reasons for changes or additional comments. If there is no need to improve, simply return the content that user enter."

def analyzeCode(inputCode):
    analyzeResult = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {
                    "role": "system",
                    "content": analyst,
                },
                {
                    "role": "user",
                    "content": inputCode,
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
        
        anaList = analyzeCode(code)
        print ( anaList + "\n")
        
        optimizedResult = optimizeCode(code , anaList)
        print ( optimizedResult + "\n")
        
        result = f"{optimizedResult}"
        # Return the processed result to the frontend
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

optimizedResult = optimizeCode("test",)
print ( optimizedResult + "\n")
if __name__ == "__main__":
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    app.run(host='0.0.0.0', port=5000, ssl_context=context)