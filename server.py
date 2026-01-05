from flask import Flask, request, jsonify
import random
import time
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)

otp_store = {}

EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

OTP_EXPIRY = 60
MAX_RESEND = 3

def send_email(to, otp):
    msg = EmailMessage()
    msg.set_content(f"""
Your VibeFetch OTP is: {otp}

Valid for {OTP_EXPIRY} seconds.
Do not share this OTP.
""")
    msg["Subject"] = "VibeFetch OTP"
    msg["From"] = EMAIL
    msg["To"] = to

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL, APP_PASSWORD)
    server.send_message(msg)
    server.quit()

@app.route("/")
def home():
    return "VibeFetch OTP Backend LIVE"

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    now = time.time()

    if email in otp_store:
        if otp_store[email]["count"] >= MAX_RESEND:
            return jsonify({"error": "Resend limit exceeded"}), 429
        otp_store[email]["count"] += 1
    else:
        otp_store[email] = {"count": 1}

    otp = str(random.randint(100000, 999999))
    otp_store[email]["otp"] = otp
    otp_store[email]["time"] = now

    send_email(email, otp)
    return jsonify({"message": "OTP sent"})

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if email not in otp_store:
        return jsonify({"error": "OTP not found"}), 400

    record = otp_store[email]

    if time.time() - record["time"] > OTP_EXPIRY:
        return jsonify({"error": "OTP expired"}), 400

    if otp != record["otp"]:
        return jsonify({"error": "Invalid OTP"}), 400

    del otp_store[email]
    return jsonify({"message": "OTP verified"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
