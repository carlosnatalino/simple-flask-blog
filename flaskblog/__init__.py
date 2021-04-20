import datetime
from logging.config import dictConfig
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flaskext.markdown import Markdown
from sqlalchemy import event

# configuring the logging
# for more info, check:
# https://docs.python.org/3.8/howto/logging.html
# https://docs.python.org/3/library/logging.html
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] [%(levelname)s] [%(name)s] [%(module)s:%(lineno)s] - %(message)s',
    }},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'to_file': {
                'level': 'DEBUG',
                'formatter': 'default',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'messages.log',
                'maxBytes': 5000000,
                'backupCount': 10
            },
    },
    'root': {
        'level': 'DEBUG',  # TODO: select here the level of logging that you want
        'handlers': ['console', 'to_file']
    }
})

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'  # change and create your own key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# see more at: https://flask.palletsprojects.com/en/1.1.x/config/#SEND_FILE_MAX_AGE_DEFAULT
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # option to be used during the development phase, prevents caching

app.config['SQLALCHEMY_ECHO'] = False  # option for debugging -- should be set to False for production

# this line is to be used if you are considering uploading large files
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# this function activates stricter handling foreign keys
def _fk_pragma_on_connect(db_api_con, con_record):
    db_api_con.execute('pragma foreign_keys=ON')


db = SQLAlchemy(app)
event.listen(db.engine, 'connect', _fk_pragma_on_connect)


# this function makes the web service api to be accessible only for the requests with valid tokens
@app.before_request
def before():
    if request.path.startswith('/api') \
            and request.path != '/api/token/public':
        # if the request goes to the API, and is different from the one to get a token, token should match
        if request.is_json and 'Authorization' in request.headers: # only JSON requests are allowed
            from flaskblog.models import Token
            token_string = request.headers['Authorization'].split(' ')[1]
            token = Token.query.filter_by(token=token_string).all()
            now = datetime.datetime.now()
            if len(token) == 0:
                abort(403)
            elif token[0].date_expired < now:
                abort(403)
        else:
            return abort(403)

    # limiting the addresses to only local and Chalmers network
    if not request.remote_addr.startswith('127.0.0') and not request.remote_addr.startswith('129.16.'):
        print('DENIED:', request.remote_addr, request.headers)
        abort(403)  # forbidden


# option to be used during the development phase, prevents caching
# comment when using it in production
# for more info check: https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.after_request
# and https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


bcrypt = Bcrypt(app)
Markdown(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes
from flaskblog import routesapi  # option that loads the routesapi file containing the web service implementation
