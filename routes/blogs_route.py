from flask import Blueprint, jsonify, render_template, request
import uuid
import status
from auth import basic_auth
from main import mysql

blogs = Blueprint('blogs', __name__)


@blogs.route('/blogs')
def just_check():
    """Rendering blogs html content"""
    return render_template('/blogs/index.html')


@blogs.route('/blogs/all', methods=['GET'])
def get_all_blogs():
    """Get all blogs data, limited to 30 records per call"""
    try:
        # Create a cursor object to execute SQL queries
        cur = mysql.connection.cursor()

        # SQL query to get the latest 30 records ordered by timestamp
        query = """
            SELECT blog_id, title, short_description, timestamp, description, image, image_alt
            FROM blogs
            ORDER BY timestamp DESC
            LIMIT 30
        """
        cur.execute(query)

        # Fetch the data from the database
        results = cur.fetchall()
        cur.close()

        # Convert the results to a list of dictionaries
        blog_data = []
        for row in results:
            blog = {
                'blog_id': row[0],
                'title': row[1],
                'short_description': row[2],
                'timestamp': row[3].strftime('%Y-%m-%d %H:%M:%S'),  # Formatting the timestamp
                'description': row[4],
                'image': row[5],
                'image_alt': row[6]
            }
            blog_data.append(blog)

        return jsonify(blog_data), status.HTTP_200_OK

    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR


@blogs.route('/blogs/<string:blog_id>', methods=['GET'])
def get_blog_by_id(blog_id):
    """Get specific blog data"""
    try:
        # Create a cursor object to execute SQL queries
        cur = mysql.connection.cursor()

        # SQL query to get the specific blog by blog_id, excluding trigrams_search
        query = """
            SELECT blog_id, title, short_description, timestamp, description, image, image_alt
            FROM blogs
            WHERE blog_id = %s
        """
        cur.execute(query, (blog_id,))

        # Fetch the data from the database
        result = cur.fetchone()
        cur.close()

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
            return jsonify({'error': 'Title parameter is required'}), status.HTTP_400_BAD_REQUEST  # HTTP 400 Bad Request

        # Use '%' wildcards to perform a partial match in the SQL query
        search_term = f"%{title.lower()}%"

        # Create a cursor object to execute SQL queries
        cur = mysql.connection.cursor()

        # SQL query to search for blogs by title using the LIKE operator
        query = """
            SELECT blog_id, title, short_description, timestamp, description, image, image_alt
            FROM blogs
            WHERE LOWER(title) LIKE %s
            LIMIT 18
        """
        cur.execute(query, (search_term,))

        # Fetch the data from the database
        results = cur.fetchall()
        cur.close()

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


@blogs.route('/blogs/create', methods=['POST'])
@basic_auth.required
def create_blog():
    """Create a blog"""
    try:
        # Get data from request
        data = request.json
        title = data.get('title')
        short_description = data.get('short_description')
        description = data.get('description')
        image = data.get('image')
        image_alt = data.get('image_alt')

        # Validate all of the above must not be empty
        if not all([title, description, short_description, image, image_alt]):
            return (
                jsonify({
                    'message': 'Invalid request parameter'
                }),
                status.HTTP_400_BAD_REQUEST
            )

        # Generate Blog id
        blog_id = str(uuid.uuid4())

        # Insert blog data into the MySQL database
        cur = mysql.connection.cursor()
        insert_query = """
            INSERT INTO blogs
            (blog_id, title, short_description, timestamp, description, image, image_alt)
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """
        cur.execute(insert_query, (blog_id, title, short_description, description, image, image_alt))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Successfully created a document', 'blog_id_created': blog_id}), status.HTTP_201_CREATED

    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR


@blogs.route('/blogs/delete/<string:id>', methods=['DELETE'])
@basic_auth.required
def delete_blog_by_id(id):
    """Delete a blog by id"""
    try:
        # Create a cursor to interact with the MySQL database
        cur = mysql.connection.cursor()

        # Execute the query to delete the blog by blog_id
        cur.execute("DELETE FROM blogs WHERE id = %s", (id,))

        # Commit the transaction
        mysql.connection.commit()

        # Check the number of rows affected (i.e., whether a blog was deleted or not)
        if cur.rowcount == 0:
            raise Exception("No document found")

        # Close the cursor
        cur.close()

        return jsonify({'message': 'Document deleted successfully'}), status.HTTP_204_NO_CONTENT

    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR
