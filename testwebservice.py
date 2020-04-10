# This file is meant to test the functionalities of the API built in this software.
# Official documentation: https://requests.readthedocs.io/en/master/
import requests
import json

# definitions of host and port
host = 'localhost'
port = 4000

fail = False # keeps track if any of the tests had failed

# step 1: get the token
print('requesting token')
reply = requests.get(f'http://{host}:{port}/api/token/public')
if reply.status_code == 200:
    print('\trequest successful')
    auth = reply.json()
    token = auth['token'] # extracts the token out of the response
    print('\tMy authentication token is:', token)
else:
    print('\ttoken request was not successful')
    fail = True

# step 2: getting information about the web service

req_headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'
               }

print('\n\nrequesting description of the api')
reply = requests.get(f'http://{host}:{port}/api/', headers=req_headers)

print('\tStatus:', reply.status_code)
if reply.status_code == 200:
    print('\tAPI description')
    print('\t', reply.json())
elif reply.status_code == 403:
    print('\tYour credentials have expired! Get new ones!')
    fail = True
else:
    print('\tUnknown error while getting description of the api:', reply.status_code)

# step 3: getting a list of posts
print('\n\nGetting a list of posts')
req_headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'
              }

reply = requests.get(f'http://{host}:{port}/api/posts', headers=req_headers)

print('\tCode:', reply.status_code)

if reply.status_code == 200:
    for post in reply.json():
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
elif reply.status_code == 403:
    print('\tGET LIST: Your credentials have expired! Get new ones!')
    fail = True
else:
    print('\tGET LIST: There was an error:', reply.status_code)
    fail = True

# step 4: inserting a new post
print('\n\nInserting a post')
req_headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'
              }

post = {'title': 'Define here the title of the student llllll',
       'content_type': 'markdown',
       'content': 'Define here the content you want in the post',
       'user': 1}

reply = requests.post(f'http://{host}:{port}/api/posts', headers=req_headers, data=json.dumps(post))

if reply.status_code == 201:
    print('\tCreated with success')
    post_received = reply.json()
    print('\tPost created:')
    post_id = post_received['id']
    print('\t\tid:', post_received['id'])
    print('\t\ttitle:', post_received['title'])
elif reply.status_code == 403:
    print('\tINSERT: Your credentials have expired! Get new ones!')
    fail = True
else:
    print('\tINSERT: There was an error:', reply.status_code)
    fail = True


# step 5: getting a specific post
print('\n\nGetting a post')
req_headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'
              }

reply = requests.get(f'http://{host}:{port}/api/post/{post_id}', headers=req_headers)

if reply.status_code == 200:
    print('\tPost found:')
    for key, value in reply.json().items():
        print('\t\t', key, ':', value)
elif reply.status_code == 404:
    print('\tFIND POST: Post not found! Try another id!')
    fail = True
elif reply.status_code == 403:
    print('\tFIND POST: Your credentials have expired! Get new ones!')
    fail = True
else:
    print('\tFIND POST: There was an error:', reply.status_code)
    fail = True

# step 6: replacing a post
print('\n\nReplacing a post')
req_headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'
              }

post = {'title': 'Define here the title of the student llllll',
       'content_type': 'markdown',
       'content': 'Define here the content you want in the post',
       'user': 1}

reply = requests.put(f'http://{host}:{port}/api/post/{post_id}', headers=req_headers, data=json.dumps(post))

if reply.status_code == 200:
    print('\tReplaced with success')
    post_received = reply.json()
    print('\tPost replaced:')
    print('\t\tid:', post_received['id'])
    print('\t\ttitle:', post_received['title'])
elif reply.status_code == 403:
    print('\tREPLACE: Your credentials have expired! Get new ones!')
    fail = True
else:
    print('\tREPLACE: There was an error:', reply.status_code)
    print('\t', reply.text)
    fail = True

# step 7: editing a post
print('\n\nEditing a post')
req_headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'
              }

post = {'title': 'Define here the title of the student llllll -- replaced',
#        'content_type': 'markdown',
#        'content': 'Define here the content you want in the post',
#        'user': 1
       }

reply = requests.patch(f'http://{host}:{port}/api/post/{post_id}', headers=req_headers, data=json.dumps(post))

if reply.status_code == 200:
    print('\tUpdated with success')
    post_received = reply.json()
    print('\tPost edited:')
    print('\t\tid:', post_received['id'])
    print('\t\ttitle:', post_received['title'])
elif reply.status_code == 403:
    print('\tUPDATE: Your credentials have expired! Get new ones!')
    fail = True
else:
    print('\tUPDATE: There was an error:', reply.status_code)
    print('\t', reply.text)
    fail = True

# step 8: deleting a post
print('\n\nDeleting a post')
req_headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'
              }

reply = requests.delete(f'http://{host}:{port}/api/post/{post_id}', headers=req_headers)

if reply.status_code == 200:
    print('\tPost deleted:')
    for key, value in reply.json().items():
        print('\t\t', key, ':', value)
elif reply.status_code == 404:
    print('\tDELETE: Post not found! Try another id!')
    fail = True
elif reply.status_code == 403:
    print('\tDELETE: Your credentials have expired! Get new ones!')
    fail = True
else:
    print('\tDELETE: Unknown error:', reply.status_code)
    fail = True
    print(reply.text)


if not fail:
    print('\n\nTHE TESTS WERE SUCCESSFUL')
else:
    print('\n\nTHE TESTS WERE NOT SUCCESSFUL')