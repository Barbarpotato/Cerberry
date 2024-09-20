from flask import  render_template
from routes.blogs_route import blogs
from routes.forms_route import forms
from main import app

app.register_blueprint(blogs)
app.register_blueprint(forms)

@app.route('/', methods=['GET'])
def get_main():
    return render_template('index.html')