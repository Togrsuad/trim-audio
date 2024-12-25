import os
from flask import Flask, render_template

app = Flask(__name__)

# Root route for the home page
@app.route('/')
def home():
    return "Welcome to Trim Audio! The app is running successfully."

if __name__ == '__main__':
    # Use PORT environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
