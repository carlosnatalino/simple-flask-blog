import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentForm
from flaskblog.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    if 'keyword' in request.args:
        keyword = request.args['keyword']
        # search the posts using the keyword
        posts = Post.query.filter(Post.title.like(f'%{keyword}%')).order_by(Post.date_posted.desc()).all()
        app.logger.debug(f'searching by `{keyword}` returned {len(posts)} posts')
    else:
        posts = Post.query.order_by(Post.date_posted.desc()).all()
        app.logger.debug(f'index without searching returned {len(posts)} posts')
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
            app.logger.debug('New user created successfully.')
            flash('Your account has been created! You are now able to log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.critical(f'Error while creating the user {user}')
            app.logger.exception(e)
            flash('The system encountered a problem while creating your account. Try again later.', 'danger')
    return render_template('register.html',
                           title='Register',
                           form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html',
                           title='Login',
                           form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_compressed_picture(form_picture):
    """
    Function that gets the file contained in the parameter `form_picture`, compresses it to a 125x125 pixels image,
    and saves it to the `static/profile_pics` folder.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static', 'profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def save_raw_picture(form_picture):
    """
    Function that gets the file contained in the parameter `form_picture`,
    and saves it to the `static/profile_pics` folder.
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static', 'profile_pics', picture_fn)

    form_picture.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            # picture_file = save_compressed_picture(form.picture.data)
            picture_file = save_raw_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        try:
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
        except Exception as e:
            db.session.rollback()
            app.logger.critical(f'Error while updating your account. {current_user}')
            app.logger.exception(e)
            flash('There was an error while updating your account. Try again later.', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html',
                           title='Account',
                           form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        created_post = Post(title=form.title.data,
                            content_type=form.content_type.data,
                            content=form.content.data,
                            author=current_user)
        db.session.add(created_post)
        try:
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            app.logger.critical(f'Error while inserting a new post: {created_post}')
            app.logger.exception(e)
            flash('There was an error while creating your post. Try again later.', 'danger')
    return render_template('create_post.html',
                           title='New Post',
                           form=form,
                           legend='New Post')


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    current_post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:  # you can only comment if you're logged in
            new_comment = Comment(content=form.content.data,
                                  author=current_user,
                                  post=current_post)
            db.session.add(new_comment)
            try:
                db.session.commit()
                form.content.data = ""
                flash('Your comment has been created!', 'success')
            except Exception as e:
                db.session.rollback()
                app.logger.critical(f'Error while creating the comment: {new_comment}')
                app.logger.exception(e)
                flash('There was an error while creating your comment. Try again later.', 'danger')
        else:
            flash('You are not logged in. You need to be logged in to be able to comment!', 'danger')
    return render_template('post.html',
                           title=current_post.title,
                           post=current_post,
                           form=form)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post_to_update = Post.query.get_or_404(post_id)
    if post_to_update.author != current_user:
        abort(403)  # only the owner of the post can edit it!
    form = PostForm()
    if form.validate_on_submit():
        post_to_update.title = form.title.data
        post_to_update.content = form.content.data
        post_to_update.content_type = form.content_type.data
        try:
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('post', post_id=post_to_update.id))
        except Exception as e:
            db.session.rollback()
            app.logger.critical(f'Error while updating the post: {post_to_update}')
            app.logger.exception(e)
            flash('There was an error while updating your post. Try again later!', 'danger')
    elif request.method == 'GET':
        form.title.data = post_to_update.title
        form.content.data = post_to_update.content
        form.content_type.data = post_to_update.content_type
    return render_template('create_post.html',
                           title='Update Post',
                           form=form,
                           legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    if post_to_delete.author != current_user:
        abort(403)  # only the author can delete their posts
    # first we need to delete all the comments
    # this can be also configured as "cascade delete all"
    # so that all comments are deleted automatically
    # I personally prefer explicitly deleting the child rows
    # see models.py file, class Comment
    for comment in post_to_delete.comments:
        db.session.delete(comment)
    db.session.delete(post_to_delete)
    try:
        db.session.commit()
        flash('Your post has been deleted!', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        app.logger.critical(f'Error while deleting the post: {post_to_delete}')
        app.logger.exception(e)
        flash('There was an error while deleting your post. Try again later!', 'danger')
