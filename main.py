from flask import Flask
from auth import basic_auth
from dotenv import load_dotenv
from flask_cors import CORS
import os

def create_app():

    app = Flask(__name__)
    CORS(app)

    # Load environment variables from .env file
    load_dotenv()

    app.config['BASIC_AUTH_USERNAME'] = os.getenv('BASIC_AUTH_USERNAME')
    app.config['BASIC_AUTH_PASSWORD'] = os.getenv('BASIC_AUTH_PASSWORD')

    # Configure BasicAuth extension after creating the Flask app
    basic_auth.init_app(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)