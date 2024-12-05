import logging
log_filename = "azure_openai_requests.log"
# Enable logging for requests
logging.basicConfig(
    level=logging.DEBUG,  # Log level to capture debug messages
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()]  # Output to both file and console
)

from flask import Flask, request, jsonify, render_template, session
import requests
import os
from Controllers.chat_controller import ChatController
chat_controller = ChatController()

from Controllers.scrap_data_controller import ScrapDataController
scrap_web_controller = ScrapDataController()

from Models.chat_model import ChatModel
chat_model = ChatModel()

from RAGs.scrapping_rag import ScrappingRag
scrap_rag = ScrappingRag()

from LANGCHAIN.chat_langchain import ChatLangchain
chat_langchain = ChatLangchain()
 
faiss_index = None
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
    global faiss_index
    faiss_index = scrap_rag.create_faiss_index(scraped_data)
 
    return jsonify({
            "message": "Webpage scraped and data stored in FAISS.",
            "scraped_data": scraped_data, # Return the scraped data in the response
        })

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("user_input")
    qa_chain = chat_langchain.initialize_langchain()
    return chat_controller.handle_chat_requests(user_input,qa_chain)

if __name__ == '__main__':
    app.run(debug=True)