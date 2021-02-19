"""
file that implements the web service part of the project.
for more information about REST methods and their responsibilities,
visit: https://www.restapitutorial.com/lessons/httpmethods.html
or https://www.w3schools.in/restful-web-services/rest-methods/
"""

import sys
from flask import request, jsonify, abort
from flaskblog import app, db, bcrypt
from flaskblog.models import Token, Post, User
import datetime


# method used to create a token that can be used for some time defined by the delta
@app.route('/api/token/public', methods=['POST'])
def get_token():
	data = request.form  # gets the JSON sent by the user

	if 'email' not in data or 'password' not in data:
		# in this case, we do not have enough information to perform a login
		return abort(400)  # HTTP code 400: bad request

	user = User.query.filter_by(email=data['email']).first()
	if user and bcrypt.check_password_hash(user.password, data['password']):
		# if login info is correct, create a new token
		expired = datetime.datetime.now() + datetime.timedelta(minutes=60)
		token_string = bcrypt.generate_password_hash(str(expired)).decode('utf-8')
		new_token = Token(token=token_string, date_expired=expired, user_id=user.id)
		db.session.add(new_token)
		try:
			db.session.commit()
			return jsonify({'token': token_string,
							'message': 'Login successful!',
							'user_id': user.id,
							'expire': expired.strftime('%Y-%m-%d %H:%M:%S')})
		except:
			db.session.rollback()
			return abort(400)  # HTTP code 400: bad request
	else:
		info = dict(message='Login Unsuccessful. Please check email and password.')
		return jsonify(info)


# method used to inform the user of the webservice regarding its capabilities
@app.route('/api/', methods=['GET'])
def api():
	info = dict()
	info['message'] = 'This is the API to consume blog posts'
	info['services'] = []
	info['services'].append({'url': '/api/posts', 'method': 'GET', 'description': 'Gets a list of posts'})
	return jsonify(info)


# method that returns all the posts
@app.route('/api/posts', methods=['GET'])
def api_get_posts():
	posts = Post.query.all()
	return jsonify(posts)


# method that returns a specific post
@app.route('/api/post/<int:post_id>', methods=['GET'])
def api_get_post(post_id):
	post = Post.query.get_or_404(post_id)
	return jsonify(post)


# method that inserts a new post
# note that the JSON received should have the key 'user' containing the user_id
@app.route('/api/posts', methods=['POST'])
def api_create_post():
	data = request.json  # gets the JSON sent by the user

	token_string = request.headers['Authorization'].split(' ')[1]
	token = Token.query.filter_by(token=token_string).first()

	# the conditional should make sure that all the non-null attributes are present in the
	# data sent by the call
	if 'title' in data and 'content_type' in data and 'content' in data:
		post = Post(title=data['title'],
					content_type=data['content_type'],
					content=data['content'],
					user_id=token.user_id)
		db.session.add(post)
		try:
			db.session.commit()
			return jsonify(post), 201  # status 201 means "CREATED"
		except Exception as e:
			print('The WebService API experienced an error: ', e, file=sys.stderr)
			# to have more detailed exception messages, check the content of lecture 7
			db.session.rollback()
			abort(400)
	else:
		return abort(400)  # HTTP code 400: bad request


# method PUT replaces the entire object, i.e., changes all the attributes
@app.route('/api/post/<int:post_id>', methods=['PUT'])
def api_update_post(post_id):
	post = Post.query.get_or_404(post_id)  # makes sure that the post_id exists
	data = request.json

	# verifying if the token used is of the user that is author of the post
	token_string = request.headers['Authorization'].split(' ')[1]
	cur_token = Token.query.filter_by(token=token_string).first()
	if cur_token.user_id != post.user_id:
		abort(401)

	# the conditional should make sure that all the non-null attributes are present in the
	# data sent by the call
	if 'title' in data and 'content_type' in data and 'content' in data and 'user' in data:
		post.title = data['title']
		post.content_type = data['content_type']
		post.content = data['content']
		try:
			db.session.commit()
			return jsonify(post), 200
		except:
			# to have more detailed exception messages, check the content of lecture 7
			db.sesion.rollback()
			abort(400)
	else:
		return abort(400)  # HTTP code 400: bad request


# method PATCH changes only a few (not always all) the attributes of the object
@app.route('/api/post/<int:post_id>', methods=['PATCH'])
def api_replace_post(post_id):
	post = Post.query.get_or_404(post_id)
	data = request.json

	# verifying if the token used is of the user that is author of the post
	token_string = request.headers['Authorization'].split(' ')[1]
	cur_token = Token.query.filter_by(token=token_string).first()
	if cur_token.user_id != post.user_id:
		abort(401)

	# you should have at least one of the columns to be able to perform an update
	if 'title' in data or 'content_type' in data or 'content' in data:

		# the conditionals below check each of the possible attributes to be modified
		if 'title' in data:
			post.title = data['title']
		if 'content_type' in data:
			post.content_type = data['content_type']
		if 'content' in data:
			post.content = data['content']

		try:
			db.session.commit()
			return jsonify(post), 200
		except:
			# to have more detailed exception messages, check the content of lecture 7
			db.sesion.rollback()
			abort(400)
	else:
		return abort(400)  # HTTP code 400: bad request


@app.route('/api/post/<int:post_id>', methods=['DELETE'])
def api_delete_post(post_id):
	post = Post.query.get_or_404(post_id)

	# verifying if the token used is of the user that is author of the post
	token_string = request.headers['Authorization'].split(' ')[1]
	cur_token = Token.query.filter_by(token=token_string).first()
	if cur_token.user_id != post.user_id:
		abort(401)

	db.session.delete(post)
	try:
		db.session.commit()
		return jsonify({'message': f'Post {post_id} deleted'}), 200
	except:
		# to have more detailed exception messages, check the content of lecture 7
		db.session.rollback()
		abort(400)  # HTTP code 400: bad request
