from flask import Flask, render_template

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize app and extensions
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'



db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

# Import routes at the bottom to avoid circular import
import routes

if __name__ == '__main__':
    app.run(debug=True)

