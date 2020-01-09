import os
from flaskblog import db, bcrypt
from flaskblog.models import User, Post

try:
	os.remove('flaskblog/site.db')
	print('previous DB file removed')
except:
	print('no previous file found')

db.create_all()

hashed_password = bcrypt.generate_password_hash('testing').decode('utf-8')
default_user = User(username='Default', email='default@test.com', password=hashed_password)
db.session.add(default_user)
db.session.commit()

print('finalized')