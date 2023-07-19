from flask import Flask, request, session, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from flask_cors import CORS
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired, ValidationError, Length, DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from email_validator import EmailNotValidError, validate_email 
import os, re, string, secrets,sys, random, json

app = Flask(__name__)
app.secret_key = 'my_secret_key' # secret key for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # database uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # disable track modifications
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# user model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, default=lambda: random.randint(10000000, 99999999))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile_image = db.Column(db.String(120), nullable=True)
    following = db.Column(db.JSON)
    followers = db.Column(db.JSON)

    def __repr__(self):
        return '<User %r>' % self.username
    
# Liste theme of post
themes = ['Lastest News',
        'Sports',
        'Politics',
        'Animes & Mangas',
        'Sience & Tech',
        'Gaming',
        'Animals & Pets',
        'Girls',
        'Memes',
        'Food & Drinks',
        'Lifestyles',
        'Divers',
        'Motor vehicules',
        'Movies & TV',
        'Arts & Draws',
        'Music & Song']

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

# valid email
def is_valid_email(email):
    try:
        print(email, file=sys.stderr)
        valid = validate_email(email)
        print(valid, file=sys.stderr)
        print('*************', file=sys.stderr)
        email = valid.email
        return True
    except EmailNotValidError as e:
        return False

# valid username
def is_valid_username(username):
    if len(username) < 3:
        return False
    if not re.match("^[a-zA-Z0-9_-]+$", username):
        return False
    return True

# registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get form data
        username = request.form['uname']
        email = request.form['email']
        password = request.form['psw']
        # username = request.json.get('uname')
        # email = request.json.get('email')
        # password = request.json.get('psw')
        # Hash the password
        password_hash = generate_password_hash(password)
        # Get the file image
        if 'file' not in request.files:
            # Assume profile_image is the default image
            new_filename = 'default_profile_image.png'
        else:
            profile_image = request.files['file']
            # Generate a random string of 16 characters
            random_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(16))
            # Assume profile_image is the uploaded image file
            file_ext = os.path.splitext(profile_image.filename)[1]
            new_filename = random_string + '_' + username + file_ext 
            # Save the uploaded file with the new filename
            profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
        # Chech the username
        if not is_valid_username(username):
            return jsonify({'message': 'Invalid username'}), 400
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print('Username already exists. Please choose a different username.')
            return jsonify({'message':'Username already exists. Please choose a different username.'}), 400
        # Check email
        if not is_valid_email(email):
            return jsonify({'message':'Invalid Email'}), 400
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print('email already exists. Please choose a different email.')
            return jsonify({'message':'Email already exists. Please choose a different Email.'}), 400
        # create new user
        new_user = User(username = username, email = email, password = password_hash, profile_image = new_filename, followers = [], following = [])
        # add user to the database
        db.session.add(new_user)
        db.session.commit()
        # log in the user
        login_user(new_user)
        # Create a session for test
        session['email'] = username
        # redirect to home page
        return redirect(url_for('home'))
        # return jsonify({
        #     "username": current_user.username,
        #     "email": current_user.email,
        #     "img": current_user.profile_image,
        #     "following": current_user.following,
        #     "followers": current_user.followers
        # })
    # display registration form
    return jsonify({'message':'Error exists. Please retry for register.'}), 400

# login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form data 
        email = request.form['email']
        password = request.form['psw']
        # email = request.json.get('email')
        # password = request.json.get('psw')
        # find user by username
        user = User.query.filter_by(email=email).first()
        # check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            # log in the user
            login_user(user)
            # Create a session for test
            session['email'] = user.email
            # redirect to home page
            return redirect(url_for('home'))
            # return jsonify({
            #     "username": current_user.username,
            #     "email": current_user.email,
            #     "img": current_user.profile_image,
            #     "following": current_user.following,
            #     "followers": current_user.followers
            # })
        # display error message
        return jsonify({'message': 'Invalid email or password to login'}), 400
    # display login form
    return jsonify({'message': 'Error exists. Please retry for login.'}), 400

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/following')
def following():
    return jsonify(current_user.following)

@app.route('/followers')
def followers():
    return jsonify(current_user.followers)

@app.route('/follow', methods=['GET', 'POST'])
@login_required
def follow():
    user_email = str(request.form['follow-email'])
    print(f"######## email utilisé : {user_email}", file=sys.stderr)
    # Get the user to follow
    user_to_follow = User.query.filter_by(email = user_email).first()
    # Check if user exist
    if user_to_follow is None:
        return jsonify({'error': 'User not found'}), 400
    # Check if is yourself
    if user_email == current_user.email: 
        print(f"######## email utilisé {user_email} et email utilisateur {current_user.email}", file=sys.stderr)
        return jsonify({'error': 'You cannot follow yourself'}), 400
    # Add the followed user to the current user's following list
    following = json.loads(current_user.following) if current_user.following else []
    # Check if you allready following this user
    for test in following:
        print("followers {test}", file=sys.stderr)
        if test == {'email': user_to_follow.email, 'username': user_to_follow.username} :
            return jsonify({'message': f'You alredy follow {user_to_follow.username}'}), 400
    following.append({'email': user_email, 'username': user_to_follow.username})
    current_user.following = json.dumps(following)
    # Add the current user to the followed user's followers list
    followers = json.loads(user_to_follow.followers) if user_to_follow.followers else []
    followers.append({'email': current_user.email, 'username': current_user.username})
    user_to_follow.followers = json.dumps(followers)
    # Commit changes to the database
    db.session.commit()
    # Return a JSON response with the updated followers and following lists
    # return jsonify({'message': f'Following {user_to_follow.username}'}), 200
    return redirect(url_for('home'))

@app.route('/unfollow', methods=['POST'])
@login_required
def unfollow():
    unfollow_email = request.form['unfollow-email']
    # Get the user to unfollow
    print(f"######## email utilisé : {unfollow_email}", file=sys.stderr)
    user_to_unfollow = User.query.filter_by(email=unfollow_email).first()
    if user_to_unfollow is None:
        return jsonify({'error': 'User not found'}), 400
    print(f"######## User unfollow infos : {user_to_unfollow.followers}", file=sys.stderr)
    # Remove the email from the 'followers' field of the user to unfollow
    followers = json.loads(user_to_unfollow.followers)
    if current_user.email in followers:
        followers.remove(current_user.email)
    user_to_unfollow.followers = json.dumps(followers)
    # Remove the followed user from the 'following' field of the current user
    following = json.loads(current_user.following)
    for user in following:
        if user['email'] == unfollow_email:
            following.remove(user)
            break
    current_user.following = json.dumps(following)
    # Commit changes to the database
    db.session.commit()
    # Return a JSON response with the updated followers and following lists
    # return jsonify({'message': f'Unfollowed {unfollow_email}'}), 200
    return redirect(url_for('home'))

@app.route('/messages')
@login_required
def messages():
    return render_template('home.html')

@app.route('/groups')
@login_required
def groups():
    return render_template('home.html')

@app.route('/events')
@login_required
def events():
    return render_template('home.html')


@app.route('/gitfolio')
@login_required
def gitfolio():
    return render_template('home.html')

@app.route('/sassandrin')
@login_required
def sassandrin():
    return render_template('home.html')


@app.route('/profile')
@login_required
def profile():

    return render_template('home.html')

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    followers = json.loads(user.followers)
    following = json.loads(user.following)

    print(f"followers : {followers}", file=sys.stderr)
    print(f"following : {followers}", file=sys.stderr)

    return render_template('profile.html', user = user, following = following, followers = followers)

@app.route('/settings')
@login_required
def settings():
    return render_template('home.html')

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
