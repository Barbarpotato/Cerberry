from flask import Flask
from auth import basic_auth
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
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

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
        f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure BasicAuth extension after creating the Flask app
    basic_auth.init_app(app)

    return app


app = create_app()


mysql = SQLAlchemy(app)


if __name__ == '__main__':
    app.run(debug=True)
