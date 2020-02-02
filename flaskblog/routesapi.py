from flask import request, jsonify
from flaskblog import app, db, bcrypt
from flaskblog.models import User, Post

@app.route("/api/", methods=['GET'])
def api():
	if request.json:
		return "{'message': 'This is the API. It can reply in both JSON and XML.'}"
	else:
		return "This request is" + request.headers['Content-Type']

@app.route("/api/posts", methods=['GET'])
def api_home():
    if request.is_json:
    	posts = Post.query.all()
    	# return jsonify({'posts': [p.serialize for p in posts]})
    	return jsonify(posts)
    else:
    	return 'error'