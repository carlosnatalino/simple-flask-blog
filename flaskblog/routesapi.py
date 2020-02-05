from flask import request, jsonify, abort
from flaskblog import app, db, bcrypt
from flaskblog.models import User, Post


@app.route("/api/", methods=['GET'])
def api():
	if request.is_json:
		return "{'message': 'This is the API.'}"
	else:
		return abort(403)


@app.route("/api/posts", methods=['GET'])
def api_home():
	if request.is_json:
		posts = Post.query.all()
		return jsonify(posts)
	else:
		return abort(403)
