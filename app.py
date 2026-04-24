"""
app.py
------
Flask web server for the FitBuddy chatbot.

Two endpoints:
  GET  /        -> serves the chat UI (index.html)
  POST /chat    -> takes {"message": "..."} JSON, returns {"reply": "..."}

Run with:  python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from chatbot import FitBuddyBot

app = Flask(__name__)
bot = FitBuddyBot()  # Instantiate once at startup, reuse for every request


@app.route("/")
def home():
    """Serve the main chat interface."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Handle a chat message from the frontend."""
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    reply = bot.get_response(user_message)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    # debug=True auto-reloads when you edit code — handy while developing.
    # For the demo, this is fine; for production you'd turn it off.
    app.run(debug=True, host="0.0.0.0", port=5000)
