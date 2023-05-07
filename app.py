
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired, ValidationError, Length, DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from email_validator import validate_email, EmailNotValidError
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
        new_user = User(username = username, email = email, password = password_hash, profile_image = new_filename)
        # add user to the database
        db.session.add(new_user)
        db.session.commit()
        # log in the user
        login_user(new_user)
        # Create a session for test
        session['email'] = username
        # redirect to home page
        return redirect(url_for('home'))
    # display registration form
    return jsonify({'message':'Error exists. Please retry for register.'}), 400

# login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form data
        email = request.form['email']
        password = request.form['psw']
        # find user by username
        user = User.query.filter_by(email=email).first()
        # check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            # log in the user
            login_user(user)
            session['email'] = email
            # redirect to home page
            return redirect(url_for('home'))
        # display error message
        ### return render_template('index.html', err = 'Invalid username or password')
        return jsonify({'message': 'Invalid email or password to login'}), 400
    # display login form
    ### return render_template('index.html', err = 'Error exists. Please retry for login.')
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

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    # Get the user to follow
    user_to_follow = User.query.get(user_id)
    if user_to_follow is None:
        return jsonify({'error': 'User not found'}), 404
    # Update the 'followers' field of the user to follow
    followers = user_to_follow.followers
    if followers is None:
        followers = []
    # Get the current user from the global context
    followers.append({'id': current_user.id, 'username': current_user.username})
    user_to_follow.followers = json.dumps(followers)
    # Update the 'following' field of the current user
    following = current_user.following
    if following is None:
        following = []
    # Get the followed user from the global context
    following.append({'id': user_to_follow.id, 'username': user_to_follow.username})
    current_user.following = json.dumps(following)
    # Commit changes to the database
    db.session.commit()
    # Return a JSON response with the updated followers and following lists
    return jsonify({'message': f'Following {user_to_follow.username}'}), 200



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

@app.route('/projects')
@login_required
def projects():
    return render_template('home.html')

@app.route('/gitfolio')
@login_required
def gitfolio():
    return render_template('home.html')

@app.route('/sassandrin')
@login_required
def sassandrin():
    return render_template('home.html')

@app.route('/params')
@login_required
def params():
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
