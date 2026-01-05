from flask import Flask, request, jsonify
import random
import os
import requests

app = Flask(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
otp_store = {}

@app.route("/")
def home():
    return "VibeFetch OTP Backend LIVE"

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "VibeFetch <onboarding@resend.dev>",
            "to": [email],
            "subject": "Your OTP",
            "html": f"<h2>Your OTP is {otp}</h2>"
        }
    )

    if response.status_code == 200:
        return jsonify({"message": "OTP sent"})
    else:
        return jsonify({"error": "Email failed"}), 500

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if otp_store.get(email) == otp:
        del otp_store[email]
        return jsonify({"message": "OTP verified"})
    else:
        return jsonify({"error": "Wrong OTP"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
