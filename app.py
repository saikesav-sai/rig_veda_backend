import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from sloka_explorer.routes import veda_bp


load_dotenv()
app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-API-Key"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})
 
# Enable thread safety for Flask
app.config['THREADED'] = True


# Register all blueprints
app.register_blueprint(veda_bp)

@app.route('/')
def home():
    return "Welcome to the Veda Explorer API"

@app.route('/favicon.ico')
def favicon():
    return '', 204  

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
 