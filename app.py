import datetime
from bson.objectid import ObjectId
import pymongo
from markupsafe import escape
from flask import Flask, render_template, request, url_for, redirect, abort

# Create an instance of the Flask class
app = Flask(__name__)

# Connect to a MongoDB Atlas cluster and create a database and a collection
client = pymongo.MongoClient(
    "mongodb+srv://Admin2:Pass123@atlascluster.cgalopx.mongodb.net/?retryWrites=true&w=majority")
db = client.flask_db
todos = db.todos


# Define a route for adding and displaying todos
@app.route('/todo/', methods=('GET', 'POST'))
def todo():
    # If the request method is POST, retrieve the content and values from the form and insert them into the todos collection
    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        todos.insert_one({'content': content, 'degree': degree})

        # Redirect the user back to 'todo' route
        return redirect(url_for('todo'))

    # If the request method is GET, retrieve all todos from the todos collection and pass them to the todo.html template for rendering
    all_todos = todos.find()
    return render_template('todo.html', todos=all_todos)


# A route for deleting a todo
@app.post('/todo/<id>/delete/')
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('todo'))


@app.post('/todo/<id>/update')
def update(id):
    content = request.form['updated_content']
    degree = request.form['updated_degree']
    todos.update_one({'_id': ObjectId(id)}, {'$set': {'content': content, 'degree': degree}})
    return redirect(url_for('todo'))



# A route for the homepage
@app.route('/')
def hello():
    return render_template('index.html', utc_dt=datetime.datetime.utcnow())


# A route for the "Hello, World!" page
@app.route('/helloworld/')
def helloworld():
    return render_template('helloworld.html')


# A route for the "Hello, World!" page
@app.route('/about/')
def about():
    return render_template('about.html')


# A route for the comments page
@app.route('/comments/')
def comments():
    comments = ['This is the first comment.',
                'This is the second comment.',
                'This is the third comment.',
                'This is the fourth comment.'
                ]

    return render_template('comments.html', comments=comments)


# A route for capitalizing a word
@app.route('/capitalize/<word>/')
def capitalize(word):
    return '<h1>{}</h1>'.format(escape(word.capitalize()))


# A route for adding two numbers
@app.route('/add/<int:n1>/<int:n2>/')
def add(n1, n2):
    return '<h1>{}</h1>'.format(n1 + n2)


# A route for greeting a user by ID
@app.route('/users/<int:user_id>/')
def greet_user(user_id):
    users = ['Bob', 'Jane', 'Adam']
    try:
        return '<h2>Hi {}</h2>'.format(users[user_id])
    except IndexError:
        abort(404)


if __name__ == '__main__':
    app.run()
