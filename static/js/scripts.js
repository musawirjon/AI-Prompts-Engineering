function scrapeData() {
    const url = document.getElementById('url').value;  // Get the URL from the input field
    
    fetch('/scrap-webpage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url })  // Send URL in JSON format
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Webpage scraped and data stored in FAISS.") {
            console.log("Scraped Data:", data.scraped_data);
            // Display scraped content on the page or do further processing
            document.getElementById("scraped-data-container").innerHTML = `
                <h3>Scraped Data</h3>
                <p><strong>URL:</strong> ${data.scraped_data.url}</p>
                <p><strong>Content:</strong> ${data.scraped_data.content}</p>
            `;
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        alert('Error: ' + error);
    });
}
// Function to handle sending the message
function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (!userInput.trim()) return; // Don't send empty messages

    // Display user's message in the chat box
    displayMessage(userInput, 'user');

    // Clear the input field
    document.getElementById("user-input").value = "";

    // Make the POST request to the Flask API (updated to use '/chat' route)
    fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_input: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // Display bot's response in the chat box
        if (data.response) {
            displayMessage(data.response, 'bot');
        } else {
            displayMessage("Sorry, I couldn't understand that.", 'bot');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        displayMessage("Error: Something went wrong with the API.", 'bot');
    });
}

// Function to display messages in the chat box
function displayMessage(message, role) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add('message');
    messageDiv.classList.add(role === 'user' ? 'user-message' : 'bot-message');
    messageDiv.textContent = message;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
}

