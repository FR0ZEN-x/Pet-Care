from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/petcare_db"
app.config["SECRET_KEY"] = "your_secret_key"

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login_page" # Setting the login_view attribute to the login_page route.
login_manager.init_app(app) # Initializing the login_manager object with the app object.
login_manager.login_message_category = "info" # Setting the login_message_category attribute to display the message in the info category.

# Importing routes
from petcare import routes