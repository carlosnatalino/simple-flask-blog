# file that implements the web service part of the project.
# for more information about REST methods and their resposabilities,
# visit: https://www.restapitutorial.com/lessons/httpmethods.html
# or https://www.w3schools.in/restful-web-services/rest-methods/
from flask import request, jsonify, abort
from flaskblog import app, db, bcrypt
from flaskblog.models import Token, Post, User
import datetime


# method used to create a token that can be used for some time defined by the delta
@app.route('/api/token/public', methods=['GET'])
def token():
	expired = datetime.datetime.now() + datetime.timedelta(minutes=60)
	token_string = bcrypt.generate_password_hash(str(expired)).decode('utf-8')
	new_token = Token(token=token_string, date_expired=expired)
	db.session.add(new_token)
	try:
		db.session.commit()
		return jsonify({'token': token_string, 'expire': expired.strftime('%Y-%m-%d %H:%M:%S')})
	except:
		db.session.rollback()
		return abort(400)


# method used to inform the user of the webservice regarding its capabilities
@app.route('/api/', methods=['GET'])
def api():
	info = dict()
	info['message'] = 'This is the API to consume blog posts'
	info['services'] = []
	info['services'].append({'url': '/api/posts', 'method': 'GET', 'description': 'Gets a list of posts'})
	print(info)
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
	data = request.json # gets the JSON sent by the user

	# the conditional should make sure that all the non-null attributes are present in the
	# data sent by the call
	if 'title' in data and 'content_type' in data and 'content' in data and 'user' in data:
		post = Post(title=data['title'],
					content_type=data['content_type'],
					content=data['content'],
					user_id=int(data['user']))
		db.session.add(post)
		try:
			db.session.commit()
			return jsonify(post), 201 # status 201 means "CREATED"
		except:
			# to have more detailed exception messages, check the content of lecture 7
			db.session.rollback()
			abort(400)
	else:
		return abort(400) # 400 is bad request


# method PUT replaces the entire object, i.e., changes all the attributes
@app.route('/api/post/<int:post_id>', methods=['PUT'])
def api_update_post(post_id):
	post = Post.query.get_or_404(post_id) # makes sure that the post_id exists
	data = request.json

	# the conditional should make sure that all the non-null attributes are present in the
	# data sent by the call
	if 'title' in data and 'content_type' in data and 'content' in data and 'user' in data:
		post.title = data['title']
		post.content_type = data['content_type']
		post.content = data['content']
		post.user_id = data['user']
		try:
			db.session.commit()
			return jsonify(post), 200
		except:
			# to have more detailed exception messages, check the content of lecture 7
			db.sesion.rollback()
			abort(400)
	else:
		return abort(400) # bad request


# method PATCH changes only a few (not always all) the attributes of the object
@app.route('/api/post/<int:post_id>', methods=['PATCH'])
def api_replace_post(post_id):
	post = Post.query.get_or_404(post_id)
	data = request.json

	# you should have at least one of the columns to be able to perform an update
	if 'title' in data or 'content_type' in data or 'content' in data or 'user' in data:

		# the conditionals below check each of the possible attributes to be modified
		if 'title' in data:
			post.title = data['title']
		if 'content_type' in data:
			post.content_type = data['content_type']
		if 'content' in data:
			post.content = data['content']
		if 'user' in data:
			post.user_id = data['user']
		try:
			db.session.commit()
			return jsonify(post), 200
		except:
			# to have more detailed exception messages, check the content of lecture 7
			db.sesion.rollback()
			abort(400)
	else:
		return abort(400) # bad request


@app.route('/api/post/<int:post_id>', methods=['DELETE'])
def api_delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	db.session.delete(post)
	try:
		db.session.commit()
		return jsonify({'message': f'Post {post_id} deleted'}), 200
	except:
		# to have more detailed exception messages, check the content of lecture 7
		db.session.rollback()
		abort(400)

