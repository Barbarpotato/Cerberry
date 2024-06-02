import collections
collections.Callable = collections.abc.Callable
import unittest
from dotenv import load_dotenv
from app import app

BLOGS_DATA = {}

class TestApp(unittest.TestCase):


    def setUp(self):
        load_dotenv()
        self.client = app.test_client()


    def test_main_route_content_type(self):
        """Test that the main route returns the correct content type"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)  # Check if the content type is HTML
        

if __name__ == '__main__':
    unittest.main()
