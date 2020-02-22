from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flaskext.markdown import Markdown
from sqlalchemy import event
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_ECHO'] = True # option for debugging -- should be set to False for production


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')


db = SQLAlchemy(app)
event.listen(db.engine, 'connect', _fk_pragma_on_connect)


@app.before_request
def before():
    if request.path.startswith('/api') \
            and request.path != '/api/token/public':
        # if the request goes to the API, and is different from the one to get a token, token should match
        if request.is_json and 'Authorization' in request.headers: # only JSON requests are allowed
            from flaskblog.models import Token
            token_string = request.headers['Authorization'].split(' ')[1]
            token = db.session.query(Token).filter_by(token=token_string).all()
            now = datetime.datetime.now()
            if len(token) == 0:
                abort(403)
            elif token[0].date_expired < now:
                abort(403)
        else:
            return abort(403)

    # limiting the addresses
    if not request.remote_addr.startswith('127.0.0') and not request.remote_addr.startswith('129.16.'):
        print('DENIED:', request.remote_addr, request.headers)
        abort(403) # forbidden


bcrypt = Bcrypt(app)
Markdown(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes
from flaskblog import routesapi
