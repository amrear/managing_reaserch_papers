from flask_sqlalchemy import SQLAlchemy
from managing_research_papers import db

# This application has two tables in the database.
# One to store posts that are verified by the admins, and another for posts that are waiting to be verified by admin.
# Two classes are basically identical and are there to create two different tables in the database.

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    language = db.Column(db.String(256), nullable=False)
    publish_date = db.Column(db.DateTime, nullable=False)
    journal_type = db.Column(db.String(256), nullable=False)
    scientific_degree = db.Column(db.String(256), nullable=False)
    impact_factor = db.Column(db.Float, nullable=False)
    abstracting_and_indexing = db.Column(db.String(256), nullable=False)
    doi = db.Column(db.String(256), nullable=False)
    indexing_certificate_filename = db.Column(db.String(256), nullable=False)
    author_count = db.Column(db.Integer, nullable=False)
    poster_authorship = db.Column(db.String(256), nullable=False)
    poster_academic_rank = db.Column(db.String(256), nullable=False)
    poster_name = db.Column(db.String(256), nullable=False)
    poster_lastname = db.Column(db.String(256), nullable=False)
    poster_email = db.Column(db.String(256), nullable=False)
    poster_affiliation = db.Column(db.String(256), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(256))
    scientific_field = db.Column(db.String(256), nullable=False)
    journal_filename = db.Column(db.String(256), nullable=False)


class PendingPosts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    language = db.Column(db.String(256), nullable=False)
    publish_date = db.Column(db.DateTime, nullable=False)
    journal_type = db.Column(db.String(256), nullable=False)
    scientific_degree = db.Column(db.String(256), nullable=False)
    impact_factor = db.Column(db.Float, nullable=False)
    abstracting_and_indexing = db.Column(db.String(256), nullable=False)
    doi = db.Column(db.String(256), nullable=False)
    indexing_certificate_filename = db.Column(db.String(256), nullable=False)
    author_count = db.Column(db.Integer, nullable=False)
    poster_authorship = db.Column(db.String(256), nullable=False)
    poster_academic_rank = db.Column(db.String(256), nullable=False)
    poster_name = db.Column(db.String(256), nullable=False)
    poster_lastname = db.Column(db.String(256), nullable=False)
    poster_email = db.Column(db.String(256), nullable=False)
    poster_affiliation = db.Column(db.String(256), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(256))
    scientific_field = db.Column(db.String(256), nullable=False)
    journal_filename = db.Column(db.String(256), nullable=False)
