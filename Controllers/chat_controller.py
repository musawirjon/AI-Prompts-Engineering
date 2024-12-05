from flask import request, jsonify, session
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()
import os

from Models.chat_model import ChatModel 

class ChatController:
    def __init__(self):
        self.name = "Chat Controller"
        self.endpoint = os.getenv("OPENAI_API_URL")
        self.API_KEY = os.getenv("OPENAI_API_KEY")
        self.MODEL_NAME = os.getenv("MODEL_NAME")
        self.VERSION = os.getenv("VERSION")
        
    def handle_chat_requests(self,user_input,qa_chain): 
        if user_input:
            # First, retrieve context from the QA chain (which queries the FAISS index)
            relevant_context = qa_chain.invoke(user_input)
          
            chat_model = ChatModel()
            
            chat_model.dictionary_store({"role": "user", "content": user_input})
            chat_model.dictionary_store({"role": "assistant", "content": relevant_context})

            chat_history = chat_model.get_conversation()

            client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_version=self.VERSION,
                api_key=self.API_KEY
            )

            completion = client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=chat_history
            )

            bot_message = completion.choices[0].message.content
            
            chat_model.dictionary_store({"role": "assistant", "content": bot_message})

            return jsonify({"response": bot_message})