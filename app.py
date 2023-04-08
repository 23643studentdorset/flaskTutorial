import datetime
from bson.objectid import ObjectId
import pymongo
from markupsafe import escape
from flask import Flask, render_template, request, url_for, redirect, abort, json
from flask import request, redirect, session
from flask_bcrypt import Bcrypt
from functools import wraps

# Create an instance of the Flask class
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Connect to a MongoDB Atlas cluster and create a database and a collection
client = pymongo.MongoClient(
    "mongodb+srv://Admin2:Pass123@atlascluster.cgalopx.mongodb.net/?retryWrites=true&w=majority")
db = client.flask_db
todos = db.todos
users = db.users
app.secret_key = 'this is a secret key'

# Define a login_required decorator to require authentication for certain routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function

# Define a route for the registration form
@app.route('/register/')
def register():
    return render_template('register.html')

# Define a route for registering a new user
@app.route('/register/', methods=['POST'])
def register_post():
    email = request.form.get('email')
    password = request.form.get('password')
    existing_user = users.find_one({'email': email})

    # Check if user already exists
    if existing_user is None:
        hashpass = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert user into database
        users.insert_one({'email': email, 'password': hashpass})
        return redirect('/login')

    # If user already exists, redirect to registration page with error message
    return 'That email already exists!'.encode('utf-8')


# Define a route for the login form
@app.route('/login/')
def login():
    return render_template('login.html')

# Define a route for logging in a user
@app.route('/login/', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    user = users.find_one({'email': email})

    # Check if user exists and password is correct
    if user and bcrypt.check_password_hash(user['password'], password):

        # Save user's email address in a session variable
        session['user'] = user['email']
        return redirect('/todo/')
    else:
        return redirect('/register/')


# Define a route for logging out a user
@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user', None)
   return redirect('/')


# Define a route for adding and displaying todos
@app.route('/todo/', methods=('GET', 'POST'))
# Require authentication for this route
@login_required
def todo():
    # If the request method is POST, retrieve the content and values from the form and insert them into the todos collection
    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        deadline = request.form['deadline']
        created_on = datetime.datetime.utcnow()
        user = session['user']
        todos.insert_one({'content': content, 'degree': degree, 'user': user, 'created_on': created_on, 'deadline': deadline})

        # Redirect the user back to 'todo' route
        return redirect(url_for('todo'))

    # If the request method is GET, retrieve all todos from user in session
    user = session['user']
    user_todos = todos.find({'user': user})
    return render_template('todo.html', todos=user_todos, time_now=datetime.datetime.utcnow())


# A route for deleting a todo
@app.post('/todo/<id>/delete/')
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('todo'))

# A route for updating a todo
@app.post('/todo/<id>/update')
def update(id):
    content = request.form['updated_content']
    degree = request.form['updated_degree']
    deadline = request.form['deadline']
    todos.update_one({'_id': ObjectId(id)}, {'$set': {'content': content, 'degree': degree, 'deadline': deadline, 'changed_on': datetime.datetime.utcnow()}})
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
