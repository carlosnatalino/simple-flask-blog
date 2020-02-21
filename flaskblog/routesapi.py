from flask import request, jsonify, abort, make_response, Response
from flaskblog import app, db, bcrypt
from flaskblog.models import Token, Post
import datetime


@app.route('/api/token/public', methods=['GET'])
def token():
	'''
	method used to create a token that can be used for some time defined by the delta
	:return: flask.Response
	'''
	expired = datetime.datetime.now() + datetime.timedelta(seconds=120)
	token_string = bcrypt.generate_password_hash(str(expired)).decode('utf-8')
	new_token = Token(token=token_string, date_expired=expired)
	db.session.add(new_token)
	db.session.commit()
	return token_string


@app.route('/api/', methods=['GET'])
def api():
	'''
	method used to inform the user of the webservice regarding its capabilities
	:return: flask.Response
	'''
	if request.is_json and 'Authorization' in request.headers:
		token_string = request.headers['Authorization'].split(' ')[1]
		token = db.session.query(Token).filter_by(token=token_string).all()
		now = datetime.datetime.now()
		if token[0].date_expired > now:
			info = dict()
			info['message'] = 'This is the API to consume blog posts'
			info['services'] = []
			info['services'].append({'url': '/api/posts', 'method': 'GET', 'description': 'Gets a list of posts'})
			print(info)
			return jsonify(info)
		else:
			return abort(403)
	else:
		return abort(403)


@app.route('/api/posts', methods=['GET'])
def get_posts():
	'''
	method that returns a list of posts in JSON format
	:return: flask.Response
	'''
	if request.is_json and 'Authorization' in request.headers:
		token_string = request.headers['Authorization'].split(' ')[1]
		token = db.session.query(Token).filter_by(token=token_string).all()
		now = datetime.datetime.now()
		if token[0].date_expired > now:
			posts = Post.query.all()
			return jsonify(posts)
		else:
			return abort(403)
	else:
		return abort(403)


@app.route('/api/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
	'''
	Method that returns the complete information regarding a particular.
	:param post_id: post to be retrieved.
	:return: flask.Response
	'''
	if request.is_json and 'Authorization' in request.headers:
		token_string = request.headers['Authorization'].split(' ')[1]
		token = db.session.query(Token).filter_by(token=token_string).all()
		now = datetime.datetime.now()
		if token[0].date_expired > now:
			post = db.session.query(Post).get(post_id)
			if post:
				return jsonify(post), 200
			else:
				return abort(404) # 404 is not found
		else:
			return abort(403) # 403 is for forbidden
	else:
		return abort(403)


@app.route('/api/posts', methods=['POST'])
def create_post():
	'''
	Method used to insert a new post.
	The method expects a JSON with the information to be inserted.
	'''
	if request.is_json and 'Authorization' in request.headers:
		token_string = request.headers['Authorization'].split(' ')[1]
		token = db.session.query(Token).filter_by(token=token_string).all()
		now = datetime.datetime.now()
		if token[0].date_expired > now:
			data = request.json
			if 'title' in data and 'content_type' in data and 'content' in data and 'user' in data:
				post = Post(title=data['title'],
							content_type=data['content_type'],
							content=data['content'],
							user_id=int(data['user']))
				db.session.add(post)
				db.session.commit() # how would you improve this code?
				return jsonify(post), 201 # status 201 means "CREATED"
			else:
				return abort(400) # 400 is bad request
		else:
			return abort(403) # 403 is for forbidden
	else:
		return abort(403)


@app.route('/api/post/<int:post_id>', methods=['PUT', 'PATCH', 'DELETE'])
def modify_post(post_id):
	'''
	Method that centralizes modificaton operations on a particular post.
	Note that PUT and PATCH do not make a difference when using SQLAlchemy, since
	the ORM only updates the properties that were modified.
	The method expects a JSON with the information to be changed.
	:param post_id: The id of the post to be modified.
	:return: flask.Response
	'''
	if request.is_json and 'Authorization' in request.headers:
		token_string = request.headers['Authorization'].split(' ')[1]
		token = db.session.query(Token).filter_by(token=token_string).all()
		now = datetime.datetime.now()
		if token[0].date_expired > now:

			post = db.session.query(Post).get(post_id)
			print(post)
			if post:

				if request.method == 'PUT':

					data = request.json
					print(data)

					if 'title' in data and 'content_type' in data and 'content' in data and 'user' in data:
						post.title = data['title']
						post.content_type = data['content_type']
						post.content = data['content']
						post.user_id = data['user']
						db.session.commit()
						return jsonify(post), 200
					else:
						return abort(400) # bad request

				if request.method == 'PATCH':
					data = request.json
					print(data)
					if 'title' in data or 'content_type' in data or 'content' in data or 'user' in data:
						if 'title' in data:
							post.title = data['title']
						if 'content_type' in data:
							post.content_type = data['content_type']
						if 'content' in data:
							post.content = data['content']
						if 'user' in data:
							post.user_id = data['user']
						db.session.commit()
						return jsonify(post), 200
					else:
						return abort(400) # bad request
				if request.method == 'DELETE':
					db.session.delete(post)
					return jsonify({'success': True}), 200
			else:
				return abort(404)  # 404 is not found
		else:
			return abort(403) # 403 is for forbidden
	else:
		return abort(403)

