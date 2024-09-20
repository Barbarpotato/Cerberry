from flask import Flask
from auth import basic_auth
from dotenv import load_dotenv
from flask_mysqldb import MySQL
from flask_cors import CORS
import os


def create_app():

    app = Flask(__name__)

    # Mysql Setup
    CORS(app)

    # Load environment variables from .env file
    load_dotenv()

    app.config['BASIC_AUTH_USERNAME'] = os.getenv('BASIC_AUTH_USERNAME')
    app.config['BASIC_AUTH_PASSWORD'] = os.getenv('BASIC_AUTH_PASSWORD')

    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
    app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))

    # Configure BasicAuth extension after creating the Flask app
    basic_auth.init_app(app)

    return app


app = create_app()


mysql = MySQL(app)


if __name__ == '__main__':
    app.run(debug=True)
