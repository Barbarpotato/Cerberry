import collections
collections.Callable = collections.abc.Callable
import unittest
import status
from dotenv import load_dotenv
import os
import json 
from unittest.mock import patch, Mock
from app import app

FORMS_DATA = {}

class TestForms(unittest.TestCase):

    def setUp(self):
        load_dotenv()
        self.client = app.test_client()
        self.username = os.getenv('BASIC_AUTH_USERNAME')
        self.password = os.getenv('BASIC_AUTH_PASSWORD')
        global FORMS_DATA
        with open('tests/fixtures/forms.json') as json_data:
            FORMS_DATA = json.load(json_data)


    ######################################################################
    #                      T E S T   C A S E S
    ######################################################################


    def test_invalid_input_contact_us(self):
        """It should return error message when fields forms are missing"""
        response = self.client.post('/form/contact_us', json=FORMS_DATA['INVALID_CONTACT_US_DATA'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json(), {"message": "All fields are required. Property required: name, email, message"})

    @patch('routes.forms_route.db.collection')
    def test_create_contact_us(self, mock_collection):
        """It should store the contact us user information to Db"""
        # Pemalsuan objek collection

        mock_db = Mock()
        mock_collection.return_value = mock_db

        # Implementasi pemalsuan untuk metode add
        mock_add_method = mock_db.add
        mock_add_method.return_value = Mock()

        response = self.client.post('/form/contact_us', json=FORMS_DATA['VALID_CONTACT_US_DATA'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.get_json(), {"message": "Successfully Send a Message"})


    @patch('routes.forms_route.db.collection')
    def test_create_blog_exception(self, mock_data):
        """It should return an error when creating a message but failed"""
        # Mocking the collection to simulate an error during document creation
        mock_data.side_effect = Exception('Simulated error')

        response = self.client.post('/form/contact_us', json=FORMS_DATA["VALID_CONTACT_US_DATA"])

        # Assert that the response status code is 500 (internal server error)
        self.assertEqual(response.status_code, status.HTTP_500_SERVER_ERROR)

        # Assert that the response contains the expected error message
        expected_error_message = {'error': 'Simulated error'}
        self.assertEqual(response.get_json(), expected_error_message)
