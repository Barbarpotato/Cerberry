from flask import Blueprint, jsonify, request
from flask_limiter import Limiter
from main import app
from flask_limiter.util import get_remote_address
import status
from firebase_setup import initialize_firestore

forms = Blueprint('forms', __name__)

db = initialize_firestore()

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
)


@forms.route('/form/contact_us', methods=['POST'])
@limiter.limit("3 per day")
def create_contact_us():
    """Store the contact us user information to Db"""
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        # Validate all of the above must not be empty
        if not all([name, email, message]):
            return (
                jsonify({
                    'message': 'All fields are required. Property required: name, email, message'
                }),
                status.HTTP_400_BAD_REQUEST
            )

        contact_us_collection = db.collection('contact-us')
        contact_us_collection.add({
            "name": name,
            "email": email,
            "message": message
        })
        return jsonify({'message': 'Successfully Send a Message'}), status.HTTP_201_CREATED

    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR
