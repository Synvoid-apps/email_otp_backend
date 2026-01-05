from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage
import random
import os

app = Flask(__name__)

# Railway ENV variables
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

# simple in-memory OTP store
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

    # generate OTP
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    try:
        msg = EmailMessage()
        msg.set_content(f"Your OTP is {otp}")
        msg["Subject"] = "VibeFetch OTP"
        msg["From"] = SENDER_EMAIL
        msg["To"] = email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        return jsonify({"message": "OTP sent"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if email not in otp_store:
        return jsonify({"error": "OTP not found"}), 400

    if otp_store[email] == otp:
        del otp_store[email]
        return jsonify({"message": "OTP verified"})
    else:
        return jsonify({"error": "Wrong OTP"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
