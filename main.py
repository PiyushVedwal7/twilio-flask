import random
from twilio.rest import Client
from flask import Flask, request, render_template_string
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Twilio credentials (now loaded from .env file)
account_sid = os.getenv('TWILIO_ACCOUNT_SID')  # Load SID from environment
auth_token = os.getenv('TWILIO_AUTH_TOKEN')  # Load Auth Token from environment
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')  # Load Twilio phone number from environment

# Initialize Flask app
app = Flask(__name__)

# Store OTPs for validation (in-memory for simplicity)
otp_store = {}

# Initialize Twilio client
client = Client(account_sid, auth_token)

@app.route('/')
def home():
    return render_template_string("""
        <form action="/send_otp" method="POST">
            <label for="phone_number">Enter your phone number:</label>
            <input type="text" id="phone_number" name="phone_number" required>
            <button type="submit">Send OTP</button>
        </form>
    """)

@app.route('/send_otp', methods=['POST'])
def send_otp():
    phone_number = request.form['phone_number']

    # Generate OTP (a random 6-digit number)
    otp = random.randint(100000, 999999)
    
    # Save OTP in memory (in a real-world scenario, store in a more secure location)
    otp_store[phone_number] = otp
    
    # Send OTP via SMS
    message_body = f'Your OTP code is {otp}. Please enter it to proceed.'
    message = client.messages.create(
        body=message_body,
        from_=twilio_phone_number,
        to=phone_number
    )
    
    return render_template_string("""
        <form action="/verify_otp" method="POST">
            <label for="otp">Enter the OTP sent to your phone:</label>
            <input type="text" id="otp" name="otp" required>
            <input type="hidden" name="phone_number" value="{{ phone_number }}">
            <button type="submit">Verify OTP</button>
        </form>
    """, phone_number=phone_number)

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    phone_number = request.form['phone_number']
    entered_otp = request.form['otp']
    
    # Check if OTP matches
    if str(otp_store.get(phone_number)) == entered_otp:
        # OTP is correct, send a confirmation message
        message_body = 'Thanks for providing your account details. 100 have been debited from your account.'
        client.messages.create(
            body=message_body,
            from_=twilio_phone_number,
            to=phone_number
        )
        return "OTP verified successfully! Notification sent."
    else:
        return "Invalid OTP. Please try again."

if __name__ == '__main__':
    app.run(debug=True)
