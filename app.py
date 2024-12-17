import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
import requests
import os
import json
from Controllers.chat_controller import ChatController
from Controllers.scrap_data_controller import ScrapDataController
from Models.chat_model import ChatModel
from LANGCHAIN.chat_langchain import ChatLangchain

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_filename = log_dir / f"azure_openai_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,  # Changed to INFO for production
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize components
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

chat_controller = ChatController()
scrap_web_controller = ScrapDataController()
chat_model = ChatModel()
chat_langchain = ChatLangchain()

@app.route('/', methods=['GET'])
def index():
    try:
        chat_history = chat_model.get_conversation()
        return render_template('chat.html', chat_history=chat_history)
    except Exception as e:
        logger.error(f"Error loading chat history: {str(e)}")
        return render_template('chat.html', chat_history=[])

@app.route('/scrap-webpage', methods=['POST'])
def scrap_web():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
            
        scraped_data = scrap_web_controller.scrape_data(url)
        
        if not scraped_data:
            return jsonify({"error": "No data could be scraped from the URL"}), 400
            
        # Save scraped data with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_dir = Path("scraped_data")
        data_dir.mkdir(exist_ok=True)
        
        with open(data_dir / f'scraped_data_{timestamp}.json', 'w') as f:
            json.dump(scraped_data, f, indent=4)
            
        # Store the scraped data in vector store
        vector_store = chat_langchain.load_documents(
            texts=scraped_data,
            metadatas=[{"source": url, "timestamp": timestamp} for _ in scraped_data]
        )
        
        logger.info(f"Successfully scraped and stored data from {url}")
        
        return jsonify({
            "message": "Webpage scraped and data stored successfully.",
            "scraped_data": scraped_data[:5],  # Return first 5 items as preview
            "total_chunks": len(scraped_data)
        })
        
    except Exception as e:
        logger.error(f"Error in web scraping: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("user_input")
        
        if not user_input:
            return jsonify({"error": "User input is required"}), 400
            
        qa_chain = chat_langchain.initialize_langchain()
        response = chat_controller.handle_chat_requests(user_input, qa_chain)
        
        logger.info("Chat request processed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat processing: {str(e)}")
        return jsonify({"error": "An error occurred processing your request"}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development')