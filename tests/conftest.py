import pytest
from app import db  # Import your database setup

@pytest.fixture(scope='session')
def setup_database():
    # Set up and tear down the database for testing
    db.create_all()  # Example setup
    yield db
    db.drop_all()  # Example teardown
