from flask import Flask, request, session, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired, ValidationError, Length, DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, re, string, secrets

app = Flask(__name__)
app.secret_key = 'my_secret_key' # secret key for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # database uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # disable track modifications
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# user model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile_image = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username

# create login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# user loader function for login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

# home page
@app.route('/')
def index():
    return render_template('index.html')

# registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get form data
        username = request.form['uname']
        email = request.form['email']
        password = request.form['psw']
        # Hash the password
        password_hash = generate_password_hash(password)
        # Get the file image
        profile_image = request.files['file']
        # Generate a random string of 16 characters
        random_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(16))
        # Assume profile_image is the uploaded image file
        file_ext = os.path.splitext(profile_image.filename)[1]
        new_filename = random_string + file_ext
        # Save the uploaded file with the new filename
        profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename)) 

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print('Username already exists. Please choose a different username.')
            return render_template('index.html', err = 'Username already exists. Please choose a different username.')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print('email already exists. Please choose a different email.')
            return render_template('index.html', err = 'Email already exists. Please choose a different Email.')
        # create new user
        new_user = User(username = username, email = email, password = password_hash, profile_image = new_filename)
        # add user to the database
        db.session.add(new_user)
        db.session.commit()
        # log in the user
        login_user(new_user)
        # Create a session for test
        session['username'] = username
        # redirect to home page
        return redirect(url_for('home'))
    # display registration form
    return render_template('index.html', err = 'Error exists. Please retry for register.')

# login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form data
        username = request.form['uname']
        password = request.form['psw']
        # find user by username
        user = User.query.filter_by(username=username).first()
        # check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            # log in the user
            login_user(user)
            session['username'] = username
            # redirect to home page
            return redirect(url_for('home'))
        # display error message
        ### return render_template('index.html', err = 'Invalid username or password')
        return jsonify({'message': 'Invalid username or password'}), 400
    # display login form
    ### return render_template('index.html', err = 'Error exists. Please retry for fogin.')
    return jsonify({'message': 'Invalid username or password'}), 400

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/messages')
@login_required
def messages():
    return render_template('not-yet.html')

@app.route('/groups')
@login_required
def groups():
    return render_template('not-yet.html')

@app.route('/events')
@login_required
def events():
    return render_template('not-yet.html')

@app.route('/projects')
@login_required
def projects():
    return render_template('not-yet.html')

@app.route('/git')
@login_required
def git():
    return render_template('not-yet.html')

@app.route('/cloud')
@login_required 
def cloud():
    return render_template('not-yet.html')

@app.route('/sassandrin')
@login_required
def sassandrin():
    return render_template('not-yet.html')

@app.route('/params')
@login_required
def params():
    return render_template('not-yet.html')

# logout page
@app.route('/logout')
@login_required
def logout():
    # log out the user
    logout_user()
    session.pop('userneme', None)
    # redirect to home page
    return redirect(url_for('index'))

# run the app
if __name__ == '__main__':
    # create tables in the database
    db.create_all()
    app.run(debug=True)
