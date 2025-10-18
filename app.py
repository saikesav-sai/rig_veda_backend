import os

from chat_bot.routes import chat_bot
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from semantic_search.routes import semantic_search_bp
from sloka_explorer.routes import veda_bp

load_dotenv()
app = Flask(__name__)

# Configure CORS with proper settings for multiple users
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})
 
# Enable thread safety for Flask
app.config['THREADED'] = True


# Register all blueprints
app.register_blueprint(veda_bp)
app.register_blueprint(chat_bot)
app.register_blueprint(semantic_search_bp)

@app.route('/')
def home():
    return "Welcome to the Veda Explorer API"

@app.route('/favicon.ico')
def favicon():
    return '', 204  

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8008,debug=True)
 