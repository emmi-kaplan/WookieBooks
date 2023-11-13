from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from models.Book import Book
from models.User import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

class BookModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    cover_image_url = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    books = db.relationship('BookModel', backref='author', lazy=True)


# Create the tables inside application context
with app.app_context():
    db.create_all()

books = ["Name of the Wind", "A Clash of Kings"]  # Placeholder for storing books

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)

if __name__ == '__main__':
    app.run(debug=True)
