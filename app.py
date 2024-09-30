from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///announcements.db'  # Database URI
app.config['SECRET_KEY'] = 'mysecret'  # Secret key for session management

# Database and login manager initialization
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class Announcement(db.Model):
    """Model for announcements."""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))  # 'training' or 'meeting'
    title = db.Column(db.String(100))
    date = db.Column(db.String(20))
    venue = db.Column(db.String(100))

    def __repr__(self):
        return f'<Announcement {self.title}>'

class User(UserMixin, db.Model):
    """Model for users."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Secure ModelView for Flask-Admin
class SecureModelView(ModelView):
    """Secure ModelView for Flask-Admin."""
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# Flask-Admin setup
admin = Admin(app, name='NCFA Admin', template_mode='bootstrap4')
admin.add_view(SecureModelView(Announcement, db.session))

# Login manager user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    """Home route to display announcements."""
    announcements = Announcement.query.all()  # Fetch all announcements
    return render_template('index.html', announcements=announcements)

@app.route('/announcements')
def announcements():
    """Route to display all announcements."""
    announcements = Announcement.query.all()
    return render_template('announcements.html', announcements=announcements)

@app.route('/partners')
def partners():
    return render_template('partners.html')

@app.route('/advocacy')
def advocacy():
    return render_template('advocacy.html')

@app.route('/about')
def about():
    """About route to display information about the organization."""
    return render_template('about.html')

@app.route('/members')
def members():
    """Members route to display benefits and joining requirements."""
    return render_template('members.html')

@app.route('/contact')
def contact():
    """Contact route to display the contact page."""
    return render_template('contact.html')  # Ensure this template exists

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login route."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Admin logout route."""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Admin registration route."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('User already exists', 'danger')
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('User registered successfully', 'success')
        return redirect(url_for('login'))

# Create the database and tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
