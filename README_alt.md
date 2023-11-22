# Wookie Books

Wookie books is a bookstore REST API built using Python and Flask. 

The API allows users to create, update, and delete books as well as query the existing books in the database.

### How to build and run the application
<details>
  <summary>Click to expand</summary>

  #### Requirements
  - Flask
  - sqlalchemy
  - pytest

  #### Running the App
  - run  `python run_app.py` from main directory
    * This will build a SQLite database and start the Flask app
  - run  `add_test_users.py` from main directory
    * This will seed the SQLite database with users
  - run curl cmds to modify your database using the wookie books API
    * Some examples:
      * Cmd to view all books 
      `curl -X GET -H "Accept: application/json" http://127.0.0.1:5000/books/view`
      * Cmd to get user token 
      `curl -X POST -H "Content-Type: application/json" -d '{"username": "Chewbacca", "password": "i<3luke"}' http://127.0.0.1:5000/auth/login`
      * Cmd to publish book:
      `curl -X POST  -H "Authorization: Bearer <user token>" -H "Content-Type: application/json" -d @<json file location> http://127.0.0.1:5000/user/publish-book`


</details>

## Testing
- run `pytest` from main directory
    * This builds a test database and runs 16 tests checking all endpoints


