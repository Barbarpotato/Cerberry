from flask import Blueprint, jsonify, render_template, request, redirect, url_for
import uuid
import requests
from sqlalchemy import text
import status
from main import mysql

blogs = Blueprint('blogs', __name__)


# Helper function to validate the token
def validate_token():
    token = request.cookies.get("token")
    coretify_api_url = "https://coretify.vercel.app/auth"

    # Send the token to the coretify API for validation
    response = requests.post(coretify_api_url, json={"token": token})

    # If the token is invalid, return an error response
    if response.status_code != 200:
        return False, jsonify({"message": "Invalid token"}), status.HTTP_401_UNAUTHORIZED

    return True, None, None


@blogs.route('/blogs')
def blog_index():
    """Rendering blogs html content"""
    return render_template('/blogs/index.html')


@blogs.route('/blog/create/view')
def blog_create_view():
    """Rendering blogs html content"""

    # Validate token using the helper function
    is_valid, error_response, error_status = validate_token()
    if not is_valid:
        return redirect(url_for('login.login_page'))

    return render_template('/blogs/create.html')


@blogs.route('/blogs/all', methods=['GET'])
def get_all_blogs():
    """Get all blogs data, limited to 30 records per call"""
    try:
        # Raw SQL query to get the latest 30 records ordered by timestamp
        query = text("""
            SELECT blog_id, title, short_description, timestamp, description, image, image_alt
            FROM blogs
            ORDER BY timestamp DESC
            LIMIT 30
        """)

        # Execute the query
        results = mysql.session.execute(query).fetchall()

        # Convert the results to a list of dictionaries
        blog_data = []
        for row in results:
            blog_data.append({
                'blog_id': row[0],
                'title': row[1],
                'short_description': row[2],
                'timestamp': row[3].strftime('%Y-%m-%d %H:%M:%S'),  # Formatting the timestamp
                'description': row[4],
                'image': row[5],
                'image_alt': row[6]
            })

        return jsonify(blog_data), status.HTTP_200_OK

    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR


@blogs.route('/blogs/<string:blog_id>', methods=['GET'])
def get_blog_by_id(blog_id):
    """Get specific blog data"""
    try:
        # Raw SQL query to get the specific blog by blog_id
        query = text("""
            SELECT blog_id, title, short_description, timestamp, description, image, image_alt
            FROM blogs
            WHERE blog_id = :blog_id
        """)

        # Execute the query with parameter binding
        result = mysql.session.execute(query, {'blog_id': blog_id}).fetchone()

        # Check if the result is found
        if result:
            # Convert the result to a dictionary
            blog_data = {
                'blog_id': result[0],
                'title': result[1],
                'short_description': result[2],
                'timestamp': result[3].strftime('%Y-%m-%d %H:%M:%S'),  # Formatting timestamp
                'description': result[4],
                'image': result[5],
                'image_alt': result[6]
            }
            return jsonify(blog_data), status.HTTP_200_OK
        else:
            return jsonify({'message': 'Blog not found'}), status.HTTP_404_NOT_FOUND

    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR


@blogs.route('/blogs/search', methods=['GET'])
def search_blogs():
    """Search for blogs by title using MySQL LIKE"""
    try:
        title = request.args.get('title')
        if not title:
            return jsonify({'error': 'Title parameter is required'}), status.HTTP_400_BAD_REQUEST

        # Use '%' wildcards to perform a partial match in the SQL query
        search_term = f"%{title.lower()}%"

        # Raw SQL query to search for blogs by title using the LIKE operator
        query = text("""
            SELECT blog_id, title, short_description, timestamp, description, image, image_alt
            FROM blogs
            WHERE LOWER(title) LIKE :search_term
            LIMIT 18
        """)

        # Execute the query with parameter binding
        results = mysql.session.execute(query, {'search_term': search_term}).fetchall()

        # Convert the results to a list of dictionaries
        matched_docs = []
        for row in results:
            blog = {
                'blog_id': row[0],
                'title': row[1],
                'short_description': row[2],
                'timestamp': row[3].strftime('%Y-%m-%d %H:%M:%S'),  # Format timestamp
                'description': row[4],
                'image': row[5],
                'image_alt': row[6]
            }
            matched_docs.append(blog)

        return jsonify(matched_docs), status.HTTP_200_OK

    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR


@blogs.route('/blog/create', methods=['POST'])
def create_blog():
    """Create a blog"""
    try:

        # Validate token using the helper function
        is_valid, error_response, error_status = validate_token()
        if not is_valid:
            return error_response, error_status

        # Get data from request
        data = request.json
        title = data.get('title')
        short_description = data.get('short_description')
        description = data.get('description')
        image = data.get('image')
        image_alt = data.get('image_alt')

        # Validate all of the above must not be empty
        if not all([title, description, short_description, image, image_alt]):
            return jsonify({'message': 'Invalid request parameter'}), status.HTTP_400_BAD_REQUEST

        # Generate Blog ID
        blog_id = str(uuid.uuid4())

        # Raw SQL query to insert blog data into the database
        insert_query = text("""
            INSERT INTO blogs
            (blog_id, title, short_description, timestamp, description, image, image_alt)
            VALUES (:blog_id, :title, :short_description, NOW(), :description, :image, :image_alt)
        """)

        # Execute the insert query with parameter binding
        mysql.session.execute(insert_query, {
            'blog_id': blog_id,
            'title': title,
            'short_description': short_description,
            'description': description,
            'image': image,
            'image_alt': image_alt
        })
        mysql.session.commit()

        return jsonify({'message': 'Successfully created a document', 'blog_id_created': blog_id}), status.HTTP_201_CREATED

    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR


@blogs.route('/blog/delete/<string:id>', methods=['DELETE'])
def delete_blog_by_id(id):
    """Delete a blog by id"""
    try:

        # Validate token using the helper function
        is_valid, error_response, error_status = validate_token()
        if not is_valid:
            return error_response, error_status

        # Raw SQL query to delete the blog by blog_id
        delete_query = text("DELETE FROM blogs WHERE blog_id = :blog_id")

        # Execute the query with parameter binding
        result = mysql.session.execute(delete_query, {'blog_id': id})

        # Check if any rows were affected (i.e., whether a blog was deleted)
        if result.rowcount == 0:
            return jsonify({'message': 'Blog not found'}), status.HTTP_404_NOT_FOUND

        # Commit the transaction
        mysql.session.commit()

        return jsonify({'message': 'Document deleted successfully'}), status.HTTP_204_NO_CONTENT

    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR
