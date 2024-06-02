import collections
collections.Callable = collections.abc.Callable
import unittest
from requests import Response
import status
from dotenv import load_dotenv
import os
from base64 import b64encode
import json 
from unittest.mock import patch, Mock
from app import app

BLOGS_DATA = {}

class TestBlogs(unittest.TestCase):

    def setUp(self):
        load_dotenv()
        self.client = app.test_client()
        self.username = os.getenv('BASIC_AUTH_USERNAME')
        self.password = os.getenv('BASIC_AUTH_PASSWORD')
        global BLOGS_DATA
        with open('tests/fixtures/blogs.json') as json_data:
            BLOGS_DATA = json.load(json_data)


    def get_authenticated_headers(self):
        credentials = b64encode(f"{self.username}:{self.password}".encode()).decode('utf-8')
        return {'Authorization': f'Basic {credentials}'}


    ######################################################################
    #                      T E S T   C A S E S
    ######################################################################


    def test_blogs_route_content_type(self):
        """It should return the html content type in /blogs"""
        response = self.client.get('/blogs')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/html', response.content_type)  # Check if the content type is HTML


    def test_blog_create_view_content(self):
        """it should returns the html content type in /blog/create/view"""
        response = self.client.get('/blog/create/view')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/html', response.content_type)  # Check if the content type is HTML


    @patch('routes.blogs_route.get_all_blogs')
    def test_get_blogs(self, mock_data):
        """It should retrieved blogs data"""
        mock_data.return_value = Mock(status_code=status.HTTP_200_OK,
                                    spec=Response,
                                    json=Mock(return_value=BLOGS_DATA['ALL_BLOGS']))

        response = self.client.get('/blogs/all', headers=self.get_authenticated_headers())

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json) > 0, "No blogs returned")


    @patch('routes.blogs_route.db.collection')
    def test_get_blogs_failed(self, mock_data):
        """It should return error message when retrieving blogs but failed"""
        # Mocking the collection to simulate an error during retrieval
        mock_data.side_effect = Exception('Simulated error')

        response = self.client.get('/blogs/all', headers=self.get_authenticated_headers())

        # Assert that the response status code is 500 (internal server error)
        self.assertEqual(response.status_code, status.HTTP_500_SERVER_ERROR)


    @patch('routes.blogs_route.get_blog_by_id')
    def test_get_blog_by_id(self, mock_data):
        """It should return single blog"""
        mock_data.return_value = Mock(status_code=status.HTTP_200_OK,
                                    spec=Response,
                                    json=Mock(return_value=BLOGS_DATA['GET_BLOG']))

        response = self.client.get('/blog/4c2147e9-d2ec-4a4a-8fee-9b0052dc2ba8', headers=self.get_authenticated_headers())

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json), 1)

    @patch('routes.blogs_route.db.collection')
    def test_get_blog_by_id_failed(self, mock_data):
        """It should return error message when retrieving specific blog but failed"""
        # Mocking the collection to simulate an error during retrieval
        mock_data.side_effect = Exception('Simulated error')

        response = self.client.get('/blog/4c2147e9-d2ec-4a4a-8fee-9b0052dc2ba8', headers=self.get_authenticated_headers())

        # Assert that the response status code is 500 (internal server error)
        self.assertEqual(response.status_code, status.HTTP_500_SERVER_ERROR)


    @patch('routes.blogs_route.db.collection')
    def test_create_blog_success(self, mock_collection):
        """It should create a new blog"""
        # Pemalsuan objek collection
        mock_db = Mock()
        mock_collection.return_value = mock_db

        # Implementasi pemalsuan untuk metode add
        mock_add_method = mock_db.add
        mock_add_method.return_value = Mock()

        # Jalankan pengujian
        response = self.client.post('/blog/create', json=BLOGS_DATA["BLOG_DATA_POST"], headers=self.get_authenticated_headers())

        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Successfully created a document')

    @patch('routes.blogs_route.create_blog')
    def test_create_blog_missing_fields(self, mock_data):
        """It should return error message when fields are missing"""
        mock_data.return_value = Mock(status_code=status.HTTP_400_BAD_REQUEST,
                                    spec=Response,
                                    json=Mock(return_value=BLOGS_DATA['FAILED_CREATE_BLOG']))

        response = self.client.post('/blog/create', json=BLOGS_DATA['BAD_BLOG_DATA_POST'], headers=self.get_authenticated_headers())

        # Assert that the response status code is 400 (bad request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json(), BLOGS_DATA['FAILED_CREATE_BLOG'])

    @patch('routes.blogs_route.db.collection')
    def test_create_blog_exception(self, mock_data):
        """It should return an error when creating a blog but failed"""
        # Mocking the collection to simulate an error during document creation
        mock_data.side_effect = Exception('Simulated error')

        response = self.client.post('/blog/create', json=BLOGS_DATA["BLOG_DATA_POST"], headers=self.get_authenticated_headers())

        # Assert that the response status code is 500 (internal server error)
        self.assertEqual(response.status_code, status.HTTP_500_SERVER_ERROR)

        # Assert that the response contains the expected error message
        expected_error_message = {'error': 'Simulated error'}
        self.assertEqual(response.get_json(), expected_error_message)

    @patch('routes.blogs_route.delete_blog_by_id')
    def test_delete_document(self, mock_data):
        """It should delete a document"""
        created_blog = self.client.post('blog/create', json=BLOGS_DATA['BLOG_DATA_POST'], headers=self.get_authenticated_headers())

        blog = created_blog.get_json()
        blog_id = blog['blog_id_created']

        response = self.client.delete(f'/blog/delete/{blog_id}', headers=self.get_authenticated_headers())

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    @patch('routes.blogs_route.delete_blog_by_id')
    def test_delete_blog_by_id_not_documents_found(self, mock_data):
        """It should return error message document not found"""

        response = self.client.delete('/blog/delete/unidentified_id', headers=self.get_authenticated_headers())

        # Assert that the response status code is 500 (Internal Server Error)
        self.assertEqual(response.status_code, status.HTTP_500_SERVER_ERROR)

        # Assert the response message
        expected_response_message = {'error': 'No documents found'}
        self.assertEqual(response.get_json(), expected_response_message)


    @patch('routes.blogs_route.db.collection')
    def test_delete_document_failed(self, mock_data):
        """It should return error message when deleting a specific blog but failed"""
        # Mocking the collection to simulate an error during document creation
        mock_data.side_effect = Exception('Simulated error')

        response = self.client.delete('/blog/delete/21abc', headers=self.get_authenticated_headers())

        # Assert that the response status code is 500 (Internal Server Error)
        self.assertEqual(response.status_code, status.HTTP_500_SERVER_ERROR)


if __name__ == '__main__':
    unittest.main()
