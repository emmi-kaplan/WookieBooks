from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # Relationship with books
    user_books = db.relationship('BookModel', backref='author', lazy=True)
    # Optional pseudonym for the author
    author_pseudonym = db.Column(db.String(50), unique=True, nullable=True)

    @property
    def display_name(self):
        # use the author_pseudonym if provided (not null) else use the name property
        return self.author_pseudonym or self.username
