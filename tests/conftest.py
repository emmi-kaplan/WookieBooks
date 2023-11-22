import pytest
from create_app import create_app
from models import db as _db, UserModel, BookModel

@pytest.fixture(scope='session')
def test_app():
    app = create_app('testing')  # Load a test configuration for the app
    with app.app_context():
        _db.create_all()

        # Insert test users
        test_users = [
            UserModel(
                id=1,
                username='Lohgarra',
                password='KashyyykRulez'),
            UserModel(
                id=2,
                username='Chewbacca',
                password='i<3luke',
                author_pseudonym='Chewy'),
            UserModel(
                id=3,
                username='_Darth Vader_',
                password='lukeiamurfather',
                author_pseudonym='Anakin'),
        ]

        # Add test users to the database and commit changes
        for user in test_users:
            _db.session.add(user)

        # Insert test books
        test_books = [
            BookModel(
                id=1,
                title="Harry Potter and the Sorcerer's Stone",
                description="Rowling's debut novel, it follows Harry Potter, a young wizard who discovers his magical heritage on his eleventh birthday, when he receives a letter of acceptance to Hogwarts School of Witchcraft and Wizardry",
                author_id=1,
                cover_image_url="https://example.com/sample_image.jpg",
                price=19.99),
            BookModel(
                id=2,
                title="Harry Potter and the Chamber of Secrets",
                description="The thrilling sequel to Harry Potter and the Sorcerer' Stone",
                author_id=1,
                cover_image_url="https://example.com/sample_image.jpg",
                price=19.99),
            BookModel(
                id=3,
                title="Project Hail Mary",
                description="Space aliens and crazy pseudo-science, same author as The Martain,highly recommend",
                author_id=2,
                cover_image_url="https://example.com/sample_image.jpg",
                price=16.99),
            BookModel(
                id=99,
                title="Delete Me Please",
                description="Please delete me I don't wanna be a book",
                author_id=1,
                cover_image_url="https://example.com/sample_image.jpg",
                price=0.99),
        ]
        for book in test_books:
            _db.session.add(book)
        _db.session.commit()

        yield app
        _db.drop_all()

@pytest.fixture(scope='function')
def authenticated_client(test_app):
    """Creates a client that has a JWT for testing protected endpoints."""
    client = test_app.test_client()

    # Perform authentication to get JWT token
    credentials = {'username': 'Lohgarra', 'password': 'KashyyykRulez'}
    response = client.post('/auth/login', json=credentials)
    jwt_token = response.json['access_token']

    # Return client including the JWT in the header
    return client, jwt_token

@pytest.fixture
def test_client(test_app):
    with test_app.test_client() as client:
        with test_app.app_context():
            yield client

@pytest.fixture(scope='function')
def session(test_app, request):
    """Creates a new database session for a test."""
    _db.app = test_app
    with test_app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

def request_headers(jwt_token, xml_datatype = False, datatype_key = ''):
    """Writes request headers to be used in testing endpoints."""
    # Return xml headers if xml datatype used
    if xml_datatype:
        return {'Authorization': f'Bearer {jwt_token}', datatype_key: 'application/xml'}
    # Default return json headers
    return {'Authorization': f'Bearer {jwt_token}'}

