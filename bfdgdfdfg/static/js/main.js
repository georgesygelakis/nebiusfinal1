const form = document.getElementById("chat-form");
const chatLog = document.getElementById("chat-log");

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const userInput = document.getElementById("user-input").value;

    // Display user message
    chatLog.innerHTML += `<div class="message user">${userInput}</div>`;
    document.getElementById("user-input").value = "";

    try {
        // Send the message to the server
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput }),
        });

        const data = await response.json();
        if (data.reply) {
            // Display AI response
            chatLog.innerHTML += `<div class="message assistant">${data.reply}</div>`;
        } else {
            throw new Error(data.error || "Unknown error");
        }
    } catch (error) {
        chatLog.innerHTML += `<div class="message assistant">Error: ${error.message}</div>`;
    }

    // Scroll to the bottom
    chatLog.scrollTop = chatLog.scrollHeight;
});
