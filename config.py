class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add other common configurations here

# This is the one we're using for this example
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///books.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # Enable automatic tracking of modifications
    JWT_SECRET_KEY = 'use-the-force-luke'

# Future case. Obviously hasn't been set up yet
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/production_db'
    JWT_SECRET_KEY = 'prod-secret-key'

# Used to set up db for testing
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_books.db'
    JWT_SECRET_KEY = 'these-arent-the-droids-youre-looking-for'
