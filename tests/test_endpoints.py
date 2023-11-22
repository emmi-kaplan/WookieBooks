import pytest
import os.path
import json
from .conftest import test_app, test_client, authenticated_client, session
import xml.etree.ElementTree as ET  # For XML generation

'''Test get_books endpoint and query for json'''
def test_get_books_json(test_client):
    response = test_client.get('/books/view?title=Harry%20Potter')
    assert b'Harry Potter and the Sorcerer' in response.data
    assert b'Harry Potter and the Chamber' in response.data
    assert response.status_code == 200

'''Test get_books endpoint and query for xml'''
def test_get_books_xml(test_client):
    headers = {'Accept': 'application/xml'}
    response = test_client.get('/books/view?title=Harry%20Potter', headers=headers)
    assert b'Harry Potter and the Sorcerer' in response.data
    assert b'Harry Potter and the Chamber' in response.data
    assert not b'The Martian' in response.data
    assert response.status_code == 200

'''Test publish_book endpoint for json'''
def test_publish_book_json(authenticated_client):
    client, jwt_token = authenticated_client

    # Use the authorized client with JWT token in headers for testing protected endpoint
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # JSON payload for the POST request
    with open(os.path.join(os.path.dirname(__file__), 'test_data/book_data.json'), encoding="utf8") as data_file:
        json_data = json.load(data_file)

    response = client.post('/user/publish-book', json=json_data, headers=headers)

    # Assert the response status code and content
    assert b'Book published successfully' in response.data  # Check for success message in response
    assert response.status_code == 201  # Successful creation returns status code 201

'''Test publish_book endpoint for xml'''
def test_publish_book_xml(authenticated_client):
    client, jwt_token = authenticated_client

    # Use the authorized client with JWT token in headers for testing protected endpoint
    headers = {'Authorization': f'Bearer {jwt_token}', 'Content-Type': 'application/xml'}

    # XML payload for the POST request
    with open(os.path.join(os.path.dirname(__file__), 'test_data/book_data.xml'), encoding="utf8") as data_file:
        tree = ET.parse(data_file)
        xml_data = ET.tostring(tree.getroot(), encoding='utf-8', method='xml')

    response = client.post('/user/publish-book', data=xml_data, headers=headers)

    # Assert the response status code and content
    assert b'Book published successfully' in response.data  # Check for success message in response
    assert response.status_code == 201  # Successful creation returns status code 201

'''Test publish_book endpoint for json with bad data (missing price)'''
def test_publish_book_json_bad(authenticated_client):
    client, jwt_token = authenticated_client

    # Use the authorized client with JWT token in headers for testing protected endpoint
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # JSON payload for the POST request
    with open(os.path.join(os.path.dirname(__file__), 'test_data/book_data_bad.json'), encoding="utf8") as data_file:
        json_data = json.load(data_file)

    response = client.post('/user/publish-book', json=json_data, headers=headers)

    # Assert the response status code and content
    assert b'Missing required fields: price' in response.data  # Check missing field 'price'
    assert response.status_code == 400

'''Test publish_book endpoint for xml with bad data (missing title)'''
def test_publish_book_xml_bad(authenticated_client):
    client, jwt_token = authenticated_client

    # Use the authorized client with JWT token in headers for testing protected endpoint
    headers = {'Authorization': f'Bearer {jwt_token}', 'Content-Type': 'application/xml'}

    # XML payload for the POST request
    with open(os.path.join(os.path.dirname(__file__), 'test_data/book_data_bad.xml'), encoding="utf8") as data_file:
        tree = ET.parse(data_file)
        xml_data = ET.tostring(tree.getroot(), encoding='utf-8', method='xml')

    response = client.post('/user/publish-book', data=xml_data, headers=headers)

    # Assert the response status code and content
    assert b'Missing required fields: title' in response.data  # Check missing field 'price'
    assert response.status_code == 400

'''Test get_user_details endpoint for json'''
def test_get_user_details_json(authenticated_client):
    client, jwt_token = authenticated_client

    # Use the authorized client with JWT token in headers for testing protected endpoint
    headers = {'Authorization': f'Bearer {jwt_token}'}

    response = client.get('/user/details', headers=headers)
    assert b'Lohgarra' in response.data
    assert response.status_code == 200

'''Test get_user_details endpoint for xml'''
def test_get_user_details_xml(authenticated_client):
    client, jwt_token = authenticated_client

    # Use the authorized client with JWT token in headers for testing protected endpoint
    headers = {'Authorization': f'Bearer {jwt_token}', 'Accept': 'application/xml'}

    response = client.get('/user/details', headers=headers)
    assert b'Lohgarra' in response.data
    assert response.status_code == 200

'''Test get_user_books endpoint for json'''
def test_get_user_books_json(authenticated_client):
    client, jwt_token = authenticated_client

    # Use the authorized client with JWT token in headers for testing protected endpoint
    headers = {'Authorization': f'Bearer {jwt_token}'}

    response = client.get('/user/books', headers=headers)
    assert b'Harry Potter and the Sorcerer' in response.data
    assert b'Harry Potter and the Chamber' in response.data
    assert not b'The Martian' in response.data
    assert response.status_code == 200

'''Test get_user_books endpoint for xml'''
def test_get_user_books_xml(authenticated_client):
    client, jwt_token = authenticated_client

    # Use the authorized client with JWT token in headers for testing protected endpoint
    headers = {'Authorization': f'Bearer {jwt_token}', 'Accept': 'application/xml'}

    response = client.get('/user/books', headers=headers)
    assert b'Harry Potter and the Sorcerer' in response.data
    assert b'Harry Potter and the Chamber' in response.data
    assert not b'The Martian' in response.data
    assert response.status_code == 200

'''Test update_book endpoint for json'''
def test_update_book_json(authenticated_client):
    client, jwt_token = authenticated_client

    # Use the authorized client with JWT token in headers for testing protected endpoint
    headers = {'Authorization': f'Bearer {jwt_token}'}
    new_data = {'price': 22.59}
    response = client.put('/user/books/2', json=new_data, headers=headers)
    assert response.status_code == 200

'''Test update_book endpoint for xml'''
def test_update_book_xml(authenticated_client):
    client, jwt_token = authenticated_client

    # Use the authorized client with JWT token in headers for testing protected endpoint
    headers = {'Authorization': f'Bearer {jwt_token}', 'Accept': 'application/xml'}
    response = client.put('/user/books/3', headers=headers)
