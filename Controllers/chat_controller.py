from flask import request, jsonify, session
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
from typing import Optional

from Models.chat_model import ChatModel

"""
Potential improvements for the chat application:

1. Streaming Responses: Implement streaming for real-time response generation instead of waiting 
   for complete responses.

2. Caching: Add caching for frequently accessed documents and embeddings to improve response time.

3. Document Chunking: Implement better document chunking strategies to handle large documents more 
   effectively during the RAG process.

4. Context Window Management: Add logic to manage the conversation history length to prevent 
   exceeding token limits.

5. Error Handling & Retry Logic: Enhance error handling for API calls and add retry mechanisms 
   for failed requests.

6. Semantic Search Enhancement: Implement hybrid search combining semantic and keyword-based 
   approaches for better context retrieval.

7. User Feedback Loop: Add functionality to collect user feedback on responses to improve the 
   system over time.

8. Memory Management: Implement better memory management for the vector store to handle large 
   scale operations.

9. Multi-Modal Support: Add support for processing images and other media types alongside text.

10. Response Quality Metrics: Implement evaluation metrics to measure response quality and 
    relevance.

11. Dynamic RAG: Allow dynamic addition of new documents to the knowledge base without 
    rebuilding the entire vector store.

12. Fine-tuning: Implement periodic fine-tuning of the model based on conversation history 
    and feedback.
"""

class ChatController:
    def __init__(self):
        """Initialize the ChatController with Azure OpenAI credentials."""
        load_dotenv()
        self.name = "Chat Controller"
        self.endpoint = os.getenv("OPENAI_API_URL")
        self.API_KEY = os.getenv("OPENAI_API_KEY")
        self.MODEL_NAME = os.getenv("MODEL_NAME")
        self.VERSION = os.getenv("VERSION")
        
        # Validate required environment variables
        if not all([self.endpoint, self.API_KEY, self.MODEL_NAME, self.VERSION]):
            raise ValueError("Missing required environment variables")
            
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_version=self.VERSION,
            api_key=self.API_KEY
        )
        
        self.chat_model = ChatModel()
        
    def handle_chat_requests(self, user_input: str, qa_chain) -> dict:
        """
        Handle chat requests using RAG and QA chain for context-aware responses.
        
        Args:
            user_input: The user's input message
            qa_chain: The question-answering chain for context retrieval
            
        Returns:
            JSON response containing the bot's message
        """
        if not user_input:
            return jsonify({"error": "Empty user input"}), 400
            
        try:
            # Store user input in chat history
            self.chat_model.dictionary_store({"role": "user", "content": user_input})
            
            # Get relevant context using the QA chain and RAG
            context_response = qa_chain.invoke(user_input)
            
            # Construct prompt with context and conversation history
            chat_history = self.chat_model.get_conversation()
            
            # Generate completion using Azure OpenAI with context
            system_prompt = {
                "role": "system", 
                "content": f"You are a helpful AI assistant. Use this context to answer the question: {context_response}"
            }
            
            messages = [system_prompt] + chat_history
            
            completion = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            bot_message = completion.choices[0].message.content
            
            # Store bot response in chat history
            self.chat_model.dictionary_store({"role": "assistant", "content": bot_message})

            return jsonify({"response": bot_message})
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500