from flask import Flask, request, jsonify, render_template, session
from openai import AzureOpenAI
import requests
import os
from Controllers.chat_controller import ChatController
chat_controller = ChatController()

from Controllers.scrap_data_controller import scrapController
scrap_web_controller = scrapController()

from Models.chat_model import ChatModel
chat_model = ChatModel()

from RAGs.scrapping_rag import ScrappingRag
scrap_rag = ScrappingRag()

from LANGCHAIN.chat_langchain import ChatLangchain
chat_langchain = ChatLangchain()

qa_chain = None
# To-do: Advanced Features(Long-term Memory, Dynamic Updates)

app = Flask(__name__) 
 
@app.route('/',methods=['GET'])
def index():
    chat_history = chat_model.get_conversation()
    return render_template('chat.html', chat_history=chat_history)

@app.route('/scrap-webpage', methods=['POST'])
def scrapWeb():
    data = request.json
    url = data.get('url')
    scraped_data = scrap_web_controller.scrape_data(url)
    # Store the scraped data in FAISS
    scrap_rag.store_in_faiss(scraped_data, index)
    # Initialize LangChain with the FAISS index
    global qa_chain
    qa_chain = chat_langchain.initialize_langchain(index)
    return jsonify({"message": "Webpage scraped and data stored in FAISS."})

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("user_input")
    return chat_controller.handle_chat_request(user_input, qa_chain)

if __name__ == '__main__':
    app.run(debug=True)