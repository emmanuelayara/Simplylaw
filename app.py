from flask import Flask, render_template
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions (but don't bind them yet)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # === Configuration ===
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Make sure upload folder exists

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # === Initialize Extensions ===
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # === Import and register routes AFTER extensions are initialized ===
    from routes import register_routes
    register_routes(app)
    
    return app

# Run the app directly (for development)
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)