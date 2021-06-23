from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# The `SECRET_KEY` is used to encrypt the client side sessions.
# It's best to store it somewhere safe like environment variables.
# The `SQLALCHEMY_DATABASE_URI` stores the location of the database which in our case is a local one.
# The `SQLALCHEMY_TRACK_MODIFICATIONS` is for the Flask-SQLAlchemy ORM to stop giving warning 
# about whether or not I need to track modification.
app.config["SECRET_KEY"] = "7ba7d1127ca60956d4e8ddb4f43ac496"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from managing_research_papers import views