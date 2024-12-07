from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables from the .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# Configure the Nebius API client
client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key=os.getenv("NEBIUS_API_KEY")
)

@app.route("/")
def index():
    # Clear the conversation history when the page is loaded
    session['messages'] = []
    # Get the prompt from the query parameter, or use a default
    prompt = request.args.get('prompt', 'You are a gift-finding assistant. Ask up to 7 brief questions about the gift recipient. Each question should be based on previous answers. After gathering information, suggest one gift and provide its Amazon link. Rules: No multiple choice questions. Ask only one question at a time. Keep questions and responses to 1-2 sentences maximum.')
    session['prompt'] = prompt
    return render_template("index.html", prompt=prompt)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Retrieve the conversation history and prompt from the session
    messages = session.get('messages', [])
    prompt = session.get('prompt', 'You are a helpful assistant.')

    # Add the system message with the prompt if it's the first message
    if not messages:
        messages.append({"role": "system", "content": prompt})

    # Add the user's message to the conversation history
    messages.append({"role": "user", "content": user_message})

    try:
        # Create a chat completion request with the entire conversation history
        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct-fast",
            messages=messages,
            temperature=0.7,
            max_tokens=150,
            top_p=0.9
        )

        # Print the raw response to inspect its structure
        print("Raw response from Nebius API:", completion)

        # Check if the response is a string
        if isinstance(completion, str):
            ai_message = completion
        # If it's not a string, it should be an object with a 'choices' attribute
        elif hasattr(completion, 'choices') and len(completion.choices) > 0:
            ai_message = completion.choices[0].message.content
        else:
            # If we can't find the expected structure, return an error
            return jsonify({"error": "Unexpected response structure from API"}), 500

        # Add the AI's response to the conversation history
        messages.append({"role": "assistant", "content": ai_message})

        # Save the updated conversation history in the session
        session['messages'] = messages

        return jsonify({"reply": ai_message})

    except Exception as e:
        # Handle errors gracefully if the API request fails
        print(f"Error in chat route: {str(e)}")
        return jsonify({"error": f"API request failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)