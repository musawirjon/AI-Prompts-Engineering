from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Initialize the Flask app
app = Flask(__name__)

# Device setup (we'll use CPU, so no GPU necessary)
device = torch.device("cpu")

# Load the model and tokenizer (change the model name if needed)
model_name = "distilgpt2"  # You can change to other smaller models
model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Route for handling text generation requests
@app.route("/generate", methods=["POST"])
def generate_text():
    # Get the input JSON data (the prompt to generate text from)
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Tokenize the input prompt
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # Generate a response using the model
    with torch.no_grad():
        outputs = model.generate(inputs["input_ids"], max_length=100, num_return_sequences=1)

    # Decode and return the output text
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return jsonify({"generated_text": generated_text})

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
