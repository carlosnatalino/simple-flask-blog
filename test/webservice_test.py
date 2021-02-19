"""
This file is meant to test the functionalities of the API built in this software.
Official documentation: https://requests.readthedocs.io/en/master/
"""

import json
import random
import requests
from lorem_text import lorem

# definitions of host and port
host = 'localhost'
port = 5000


# step 1: get the token
def test_setup():
    print('requesting token')
    global token

    response = requests.post(f'http://{host}:{port}/api/token/public',
                             data={'email': 'default@test.com',
                                   'password': 'testing'})

    assert response.status_code == 200, f'The website returned status code {response.status_code}!'

    auth = response.json()

    assert 'token' in auth and 'user_id' in auth, 'The system did not return the token as expected!'

    token = auth['token']  # extracts the token out of the response

    req_headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}

    print('\n\nrequesting description of the api')
    response = requests.get(f'http://{host}:{port}/api/', headers=req_headers)

    assert response.status_code == 200, f'The webservice returned status code {response.status_code}!'


# step 2: getting a list of posts
def list_posts():
    print('\n\nGetting a list of posts')
    req_headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}

    response = requests.get(f'http://{host}:{port}/api/posts', headers=req_headers)

    assert response.status_code == 200, f'The webservice returned status code {response.status_code}!'
    assert isinstance(response.json(), list), 'The webservice response data cannot be converted into JSON!'

    for post in response.json():
        print('\tPost', post['id'])
        for key, value in post.items():
            if key == 'content':
                print('\t\t', key.ljust(15), ':', value[:50].replace('\n', ''), '...')
            elif key == 'id':
                continue
            elif isinstance(value, dict):
                print('\t\t', key, ':')
                for k2, v2 in value.items():
                    print('\t\t\t', k2.ljust(15), ':', v2)
            else:
                print('\t\t', key.ljust(15), ':', value)


# step 3: inserting a new post
def insert_post():
    print('\n\nInserting a post')
    req_headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}
    global post_id
    post = {'title': lorem.words(random.randint(3, 7)),
            'content_type': 'markdown',
            'content': 'Define here the content you want in the post'}

    response = requests.post(f'http://{host}:{port}/api/posts', headers=req_headers, data=json.dumps(post))

    # HTTP code 201 means "created"
    assert response.status_code == 201, f'The webservice returned status code {response.status_code}!'
    assert isinstance(response.json(), dict), 'The webservice should return a JSON object.'

    print('\tCreated with success')
    post_received = response.json()
    print('\tPost created:')
    post_id = post_received['id']
    print('\t\tid:', post_received['id'])
    print('\t\ttitle:', post_received['title'])


# step 4: getting a specific post
def get_specific_post():
    print('\n\nGetting a post')
    req_headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}

    response = requests.get(f'http://{host}:{port}/api/post/{post_id}', headers=req_headers)

    assert response.status_code == 200, f'The webservice returned status code {response.status_code}!'
    assert isinstance(response.json(), dict), 'The webservice should return a JSON object.'

    print('\tPost found:')
    for key, value in response.json().items():
        print('\t\t', key, ':', value)


# step 5: replacing a post
def replace_post():
    print('\n\nReplacing a post')
    req_headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'
                  }

    post = {'title': 'Define here the title of the student llllll',
           'content_type': 'markdown',
           'content': 'Define here the content you want in the post',
           'user': 1}

    response = requests.put(f'http://{host}:{port}/api/post/{post_id}', headers=req_headers, data=json.dumps(post))

    assert response.status_code == 200, f'The webservice returned status code {response.status_code}!'
    assert isinstance(response.json(), dict), 'The webservice should return a JSON object.'


# step 6: editing a post
def edit_post():
    print('\n\nEditing a post')
    req_headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'
                  }

    post = {'title': 'Define here the title of the student llllll -- replaced'}

    response = requests.patch(f'http://{host}:{port}/api/post/{post_id}', headers=req_headers, data=json.dumps(post))

    assert response.status_code == 200, f'The webservice returned status code {response.status_code}!'
    assert isinstance(response.json(), dict), 'The webservice should return a JSON object.'

    print('\tUpdated with success')
    post_received = response.json()
    print('\tPost edited:')
    print('\t\tid:', post_received['id'])
    print('\t\ttitle:', post_received['title'])


# step 7: deleting a post
def delete_post():
    print('\n\nDeleting a post')
    req_headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {token}'}

    response = requests.delete(f'http://{host}:{port}/api/post/{post_id}', headers=req_headers)

    assert response.status_code == 200, f'The webservice returned status code {response.status_code}!'
    assert isinstance(response.json(), dict), 'The webservice should return a JSON object.'

    print('\tPost deleted:')
    for key, value in response.json().items():
        print('\t\t', key, ':', value)


if __name__ == '__main__':
    test_setup()
    list_posts()
    insert_post()
    get_specific_post()
    replace_post()
    edit_post()
    delete_post()
