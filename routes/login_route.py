from flask import Blueprint, jsonify, render_template, request, redirect, make_response, url_for
import requests
import status
import os

login = Blueprint('login', __name__)

@login.route('/login')
def login_page():
    """Rendering login html content"""
    return render_template('/login/index.html', app_token= os.getenv('APP_TOKEN'))


@login.route('/login_api', methods=['POST'])
def login_api():
    """Authentication User Account"""
    try:

        data = request.json
        username = data.get('username')
        password = data.get('password')
        app_token = data.get('app_token')

        if not all([username, password, app_token]):
            return jsonify({'message': 'Invalid parameters'}), status.HTTP_400_BAD_REQUEST

        login_api_url = "https://coretify.vercel.app/login/client"

        # send the token to the coretify api
        response = requests.post(login_api_url, json={"username": username, "password": password, "app_token": app_token})

        if response.status_code != 200:
            return jsonify({"message": "Invalid username or password"}), status.HTTP_401_UNAUTHORIZED

        login_result = response.json()

        if not login_result.get('token'):
            return jsonify({"message": "Invalid username or password"}), status.HTTP_401_UNAUTHORIZED

        token = login_result.get('token')
        
        # Create a response and set the cookie
        response = make_response(redirect(url_for('blogs.blog_create_view')))  # Adjust the redirect here
        response.set_cookie('token', token)  # Set the 'token' cookie
        return response
    except Exception as error:
        print(error)
        return jsonify({'message': str(error)}), status.HTTP_500_SERVER_ERROR
