from flask import Flask, request, jsonify, render_template, session
from openai import AzureOpenAI
import requests
import os

app = Flask(__name__)

endpoint = os.getenv("OPENAI_API_URL")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
VERSION = os.getenv("VERSION")

app.secret_key = os.getenv("SECRET_KEY", "mysecretkey123") 

client = AzureOpenAI(azure_endpoint=endpoint,api_version=VERSION,api_key=API_KEY)
@app.route('/',methods=['GET'])
def index():
    if "chat_history" not in session:
        session["chat_history"] = []  # Initialize chat history if not already in session

    chat_history = session["chat_history"]
    return render_template('chat.html', chat_history=chat_history)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("user_input")
    if not user_input:
        return jsonify({"error": "Missing user_input parameter"}), 400

    # Retrieve the chat history from the session
    chat_history = session.get("chat_history", [])
    chat_history.append({"role": "user", "content": user_input})

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=chat_history
    )

    bot_message = completion.choices[0].message.content
    chat_history.append({"role": "assistant", "content": bot_message})

    return jsonify({"response": bot_message})

if __name__ == '__main__':
    app.run(debug=True)