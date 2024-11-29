from flask import jsonify
import os
import json

class ChatModel():
    def __init__(self):
        self.history_file = "conversation_history.json"
        # If the file doesn't exist, create it
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)

    def dictionary_store(self, message):
        if 'content' in message:
            message['content'] = message['content'] + "\n" 
        # Load the conversation history from the file
        with open(self.history_file, 'r') as f:
            conversation_history = json.load(f)
        
        # Append the new message to the conversation history
        conversation_history.append(message)

        # Save the updated conversation history back to the file
        with open(self.history_file, 'w') as f:
            json.dump(conversation_history, f)
    
    def get_conversation(self):
        # Load and return the conversation history from the file
        with open(self.history_file, 'r') as f:
            return json.load(f)