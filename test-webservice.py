# This file is meant to test the functionalities of the API built in this software.
# Official documentation: https://requests.readthedocs.io/en/master/
import requests

fail = False # keeps track if any of the tests had failed

# first tests the endpoint that returns all the posts
resp = requests.get('http://localhost:4000/api/posts', headers={'Content-Type': 'application/json'})
if resp.status_code == 200:
	print('request successful')
	posts = resp.json()
	for post in posts:
		print(post['id'], post['content'])
else:
	print('request was not successful')
	fail = True

if fail:
	print('THE TESTS WERE NOT SUCCESSFUL')