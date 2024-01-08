# server.py
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS
import ssl # for local https key

app = Flask(__name__)
CORS(app)
#client = OpenAI()
api_key_model_1 = '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'
api_key_model_2 = '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'

client_model_1 = OpenAI(api_key=api_key_model_1) # For gpt-3.5-turbo-A
client_model_2 = OpenAI(api_key=api_key_model_2) # For gpt-3.5-turbo-B

# SSL key's path
cert_path = 'C:/Users/whps9/ccoliu.github.io/certificate.crt'
key_path = 'C:/Users/whps9/ccoliu.github.io/private_key.key'

# Check if the server is running now. 
@app.route("/", methods=["GET"])
def index():
    return "Hello, this is the code assistance server home page!"

systemRole = "You are a programming expert. When others give you code, you assess what the code is intended for and help them fix it. You correct any bugs in the code and enhance its readability, reliability, and coding style without changing the program's functionality. Then, you return the complete source code. There is no need for explanation; just add the reason for the modification next to the modified line. If the code is perfect or you don't see any possiable improvement, simply return perfect to user, and do not explain why or what to do only mark after the changed line, simply says what's the different."

@app.route("/process_code", methods=["POST"])
def process_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        # 在這裡進行後端處理，這裡只是一個示例，你可以插入你的處理邏輯
        result = f"{code}"
        completionA = client_model_1.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": systemRole,
                },
                {
                    "role": "user",
                    "content": code,
                }
            ],
            
        )
        result = f"{completionA.choices[0].message.content}"
        
        completionB = client_model_2.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": systemRole,
                },
                {
                    "role": "user",
                    "content": result,
                }
            ],
        )
        result = f"{completionB.choices[0].message.content}"
        # 返回處理結果到前端
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    app.run(host='0.0.0.0', port=5000, ssl_context=context)
