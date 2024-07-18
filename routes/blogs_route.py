from flask import Blueprint, jsonify, render_template, request
from google.cloud import firestore
from datetime import datetime
import uuid
from firebase_setup import initialize_firestore
import status
from auth import basic_auth

blogs = Blueprint('blogs', __name__)

db = initialize_firestore()


def generate_trigrams(text):
    """Function to generate trigrams from a string for search title blog purpose"""
    text = "#" + text + "#"
    return [text[i:i+3] for i in range(len(text) - 2)]


@blogs.route('/blogs')
def get_blogs_view():
    """Rendering blogs html content"""
    return render_template('/blogs/index.html')


@blogs.route('/blog/create/view')
def blog_create_view():
    """Rendering blog create view html content"""
    return render_template('/blogs/create.html')


@blogs.route('/blogs/all', methods=['GET'])
def get_all_blogs():
    """Get all blogs data limit by 30 records per call"""
    try:
        # Query to get the latest 30 records based on the timestamp field
        blog_collection = db.collection('blog-content')
        blog_data = blog_collection.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(30).stream()
        blog_data = [doc.to_dict() for doc in blog_data]

        # Remove 'trigrams_search' field from each document
        for doc in blog_data:
            doc.pop('trigrams_search', None)

        return jsonify(blog_data), status.HTTP_200_OK
    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR


@blogs.route('/blog/<string:blog_id>', methods=['GET'])
def get_blog_by_id(blog_id):
    """Get specific blog data"""
    try:
        # Query Firestore to get the document with the specified ID
        blog_ref = db.collection('blog-content')
        query = blog_ref.where('blog_id', '==', blog_id)
        docs = query.stream()

        # Convert query results to a list of dictionaries
        blog_data = [doc.to_dict() for doc in docs]

        # Remove 'trigrams' field from each document
        for doc in blog_data:
            doc.pop('trigrams_search', None)

        return jsonify(blog_data), status.HTTP_200_OK
    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR


@blogs.route('/blogs/search', methods=['GET'])
def search_blogs():
    """Search for blogs by title using trigrams search algorithm"""
    try:
        title = request.args.get('title')
        if not title:
            return jsonify({'error': 'Title parameter is required'}), status.HTTP_400_BAD_REQUEST

        # Generate trigrams from the search term
        title_trigrams = generate_trigrams(title.lower())

        blog_collection = db.collection('blog-content')

        # Set to keep track of document IDs that have already been added
        matched_doc_ids = set()
        matched_docs = []

        # Query blog content collection to find matches limit only 9 records to show
        for trigram in title_trigrams:
            blog_docs = blog_collection.where('trigrams_search', 'array_contains', trigram).limit(18).stream()
            for doc in blog_docs:
                doc_id = doc.id
                if doc_id not in matched_doc_ids:
                    doc_dict = doc.to_dict()
                    doc_dict.pop('trigrams_search', None)  # Remove the 'trigrams' field
                    matched_docs.append(doc_dict)
                    matched_doc_ids.add(doc_id)  # Add the document ID to the set

        return jsonify(matched_docs), status.HTTP_200_OK
    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR


@blogs.route('/blog/create', methods=['POST'])
@basic_auth.required
def create_blog():
    """Create a blog"""
    try:
        data = request.json
        title = data.get('title')
        short_description = data.get('short_description')
        description = data.get('description')
        image = data.get('image')
        image_alt = data.get('image_alt')

        # Get the current timestamp
        current_time = datetime.now()

        # Format the timestamp as mm/dd/yyyy, hh::mm::ss
        current_time = current_time.strftime("%m/%d/%Y, %H:%M:%S")

        # Generate trigrams from the search engine algorithm use case
        trigrams_search = generate_trigrams(title.lower())

        # Validate all of the above must not be empty
        if not all([title, description, image, image_alt]):
            return (
                jsonify({
                    'message': 'All fields are required. Property required: title, description, image, image_alt'
                }),
                status.HTTP_400_BAD_REQUEST
            )

        # generate blog_id
        blog_id = str(uuid.uuid4())
        # Add a new blog document to Firestore
        blog_collection = db.collection('blog-content')
        blog_collection.add({
            'blog_id': blog_id,
            'title': title,
            'short_description': short_description,
            'timestamp': current_time,
            'description': description,
            'image': image,
            'image_alt': image_alt,
            'trigrams_search': trigrams_search
        })
        return jsonify({'message': 'Successfully created a document', 'blog_id_created': blog_id}), status.HTTP_201_CREATED
    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR


@blogs.route('/blog/delete/<string:blog_id>', methods=['DELETE'])
@basic_auth.required
def delete_blog_by_id(blog_id):
    """Delete a blog by id"""
    try:
        query = db.collection('blog-content').where('blog_id', '==', blog_id)
        docs = query.stream()

        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1

        if deleted_count == 0:
            raise Exception("No documents found")

        return jsonify({'message': 'Document deleted successfully'}), status.HTTP_204_NO_CONTENT

    except Exception as error:
        return jsonify({'error': str(error)}), status.HTTP_500_SERVER_ERROR
