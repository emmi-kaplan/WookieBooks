from endpoints import app, db, UserModel


# Must initialize and configure the app and database before calling
with app.app_context():
    # Create tables (if not exist)
    db.create_all()

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

    # Add test users to the database
    for user in test_users:
        db.session.add(user)

    # Commit the changes to db
    db.session.commit()

    print("Test users inserted successfully!")