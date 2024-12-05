from transformers import pipeline
from flask import jsonify

class ChatController:
    def __init__(self):
        self.nlp = pipeline("text-generation", model="gpt2")
        self.conversation_history = []

    def handle_chat_request(self, user_input, qa_chain):
        self.conversation_history.append({"role": "user", "content": user_input})

        relevant_context = qa_chain.invoke(user_input)
        self.conversation_history.append({"role": "assistant", "content": relevant_context})

        prompt = "You are a helpful AI assistant. Here is the conversation so far:\n"
        for message in self.conversation_history:
            prompt += f"{message['role']}: {message['content']}\n"
        prompt += "User: " + user_input + "\nAssistant:"

        response = self.nlp(prompt, max_length=50, num_return_sequences=1)
        bot_message = response[0]['generated_text']

        self.conversation_history.append({"role": "assistant", "content": bot_message})

        return jsonify({"response": bot_message})