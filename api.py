"""
================================
FLASK API
================================
"""
# dependencies
from flask import Flask, request, jsonify

# chatbot.py
import chatbot


app = Flask(__name__)


# ------------------------------------------------------------
# ------------------------------------------------------------
# routes

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI3000-assignment-api",
        "version": "1.0.0"
    }), 200

@app.route("/", methods=["GET"])
def home():
    """Default"""
    return "Flask AI3000-assignment-api running"

@app.route("/chat", methods=["POST"])
def chat():
    """main chatbot endpoint"""
    try:
        data = request.get_json()

        type = data.get("type")
        question = data.get("question")

        response = chatbot.chatbot(type, question)

        status = response.get("status", 200)

        if status != 200:
            return jsonify({
                "error": response.get("message", "Unknown error")
                }), status
        else:
            return jsonify({
                "response":response.get("response", "bazinga")
            }), status
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
            }), 500


# ------------------------------------------------------------
# ------------------------------------------------------------
# setup yay

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)