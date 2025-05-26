from flask import Flask, render_template
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize app and extensions
app = Flask(__name__)

# your routes, models, config, etc.


# Configure upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')


app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

# Import routes at the bottom to avoid circular import
import routes

if __name__ == '__main__':
    app.run(debug=True)

