# firebase_setup.py
import os
from dotenv import load_dotenv
from google.cloud import firestore


def initialize_firestore():
    # Load environment variables from .env file
    load_dotenv()

    # Initialize Firestore client
    project_id = os.getenv('FIREBASE_PROJECT_ID')
    private_key = os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n')
    client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
    private_key_id = os.getenv('FIREBASE_PRIVATE_KEY_ID')
    client_id = os.getenv('FIREBASE_CLIENT_ID')
    token_uri = os.getenv('FIREBASE_TOKEN_URI')

    credentials = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": client_id,
        "token_uri": token_uri
    }

    return firestore.Client.from_service_account_info(credentials)
