import os
import sys
import random
import datetime
import requests
from flaskblog import db, bcrypt, app
from flaskblog.models import User, Post, Comment
from lorem_text import lorem
from sqlalchemy.sql.expression import func

host = 'localhost'  # host where the system is running
port = 5000  # port where the process is running


def reload_database():
    try:
        response = requests.get(f'http://{host}:{port}')
        app.logger.critical('The website seems to be running. Please stop it and run this file again.')
        exit(11)
    except Exception as e:
        pass
    try:
        os.remove('flaskblog/site.db')
        app.logger.info('previous DB file removed')
    except:
        app.logger.info('no previous DB file found')

    assert not os.path.exists('flaskblog/site.db'), 'It seems that site.db was not deleted. Please delete it manually!'

    db.create_all()

    # creating two users
    hashed_password = bcrypt.generate_password_hash('testing').decode('utf-8')
    default_user1 = User(username='Default',
                         email='default@test.com',
                         image_file='another_pic.jpeg',
                         password=hashed_password)
    db.session.add(default_user1)

    hashed_password = bcrypt.generate_password_hash('testing2').decode('utf-8')
    default_user2 = User(username='Default Second',
                         email='second@test.com',
                         image_file='7798432669b8b3ac.jpg',
                         password=hashed_password)
    db.session.add(default_user2)

    hashed_password = bcrypt.generate_password_hash('testing3').decode('utf-8')
    default_user3 = User(username='Default Third',
                         email='third@test.com',
                         password=hashed_password)
    db.session.add(default_user3)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.critical('Error while committing the user insertion.')
        app.logger.exception(e)

    # testing if the users were added correctly
    assert len(User.query.all()) == 3, 'It seems that user failed to be inserted!'

    users = [default_user1, default_user2, default_user3]

    # creating posts for each user
    for user in users:

        # creating 3 to 6 posts
        for p in range(random.randint(3, 6)):

            # picking a random date for the post
            date_post = datetime.datetime.now() - \
                        datetime.timedelta(days=random.randint(1, 90),
                                           hours=random.randint(1, 23),
                                           minutes=random.randint(1, 59))

            post = Post(title=lorem.words(random.randint(3, 7)).capitalize(),
                        content_type='markdown',
                        content=lorem.paragraphs(random.randint(1, 3)),
                        date_posted=date_post,
                        author=user)

            db.session.add(post)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.critical('Error committing the posts')
                app.logger.exception(e)

            # for each post, creating 2 to 5 comments
            for c in range(random.randint(2, 5)):

                # picking a random date for the comment between the date of the post and now
                # get the difference between the date of the post and now
                diff = datetime.datetime.now() - date_post
                # compute the date of the comment using a random number from 1 to the number of seconds of the diff
                date_comment = datetime.datetime.now() - datetime.timedelta(seconds=random.randint(1, diff.seconds))

                # creating a new comment object
                comment = Comment(author=random.choice(users),  # selects a random user for the comment
                                  content=lorem.words(random.randint(10, 15)).capitalize(),
                                  date_posted=date_comment,
                                  post=post)

                # adding the comment object to the database
                db.session.add(comment)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.critical(f'Error committing the comments of post {post}')
                app.logger.exception(e)
            # testing if the comments were inserted correctly
            assert len(Comment.query.filter_by(post_id=post.id).all()) > 0, \
                f'The comments for post {post.id} were not successful!'

        # testing if the posts were inserted
        assert len(Post.query.filter_by(user_id=user.id).all()) > 0, 'Posts were not added correctly!'

    try:
        db.session.commit()
        app.logger.info('Finalized - database created successfully!')
    except Exception as e:
        db.session.rollback()
        app.logger.critical('The operations were not successful.')
        app.logger.exception(e)


def query_database():
    # listing all the posts
    posts = Post.query.all()
    print('\nAll posts:')
    for post in posts:
        print('\t', post)

    # listing all the posts in the descending order of their descending order of date_posted
    print('\nall the posts in the descending order of their descending order of date_posted')
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    for post in posts:
        print('\t', post)

    # listing posts that have a given key on the title and ordering them by their descending order of date_posted
    print('\nposts that have a given key on the title and ordering them by their descending order of date_posted')
    keyword = 'eli'
    posts = Post.query.filter(Post.title.like(f'%{keyword}%')).order_by(Post.date_posted.desc()).all()
    for post in posts:
        print('\t', post)

    # getting the 3 latest posts
    print('\nthe 3 latest posts')
    posts = Post.query.order_by(Post.date_posted.desc()).limit(3)
    for post in posts:
        print('\t', post)

    # getting 3 random posts
    print('\n3 random posts')
    posts = Post.query.order_by(func.random()).limit(3)
    for post in posts:
        print('\t', post)

    # getting posts from a user
    user = User.query.order_by(func.random()).limit(1)[0]
    print('\nposts from a user', user)
    for post in user.posts:
        print('\t', post)

    # getting all comments from a post
    post = Post.query.order_by(func.random()).limit(1)[0]
    print('\ncomments from post', post)
    for comment in post.comments:
        print('\t', comment)

    # getting a post from a comment
    comment = Comment.query.order_by(func.random()).limit(1)[0]
    print('\nDetails of comment', comment)
    print('\tAuthor:', comment.author)
    print('\tPost:', comment.post)

    # getting comments from a user
    user = User.query.order_by(func.random()).limit(1)[0]
    print('\nGetting comments from user', user)
    for comment in user.comments:
        print('\t', comment)

    # getting all posts from within a particular period
    # start_date is randomly generated
    start_date = datetime.datetime.now() - \
                 datetime.timedelta(days=random.randint(1, 90),
                                           hours=random.randint(1, 23),
                                           minutes=random.randint(1, 59))

    # end_date is randomly generated based on the start date
    end_date = start_date + \
               datetime.timedelta(days=random.randint(1, 90),
                                    hours=random.randint(1, 23),
                                    minutes=random.randint(1, 59))
    posts = Post.query.filter(Post.date_posted >= start_date).filter(Post.date_posted <= end_date).all()
    print('\nPosts created between', start_date, 'and', end_date, ':', len(posts))
    for post in posts:
        print('\t', post)

    # getting all posts from the last 30 days
    start_date = datetime.datetime.now() - \
                 datetime.timedelta(days=30)
    posts = Post.query.filter(Post.date_posted >= start_date).all()
    print('\nPosts created in the last 30 days:', len(posts))
    for post in posts:
        print('\t', post)

    # getting all comments from the last 7 days
    start_date = datetime.datetime.now() - \
                 datetime.timedelta(days=7)
    comments = Comment.query.filter(Comment.date_posted >= start_date).all()
    print('\nComments created in the last 7 days:', len(comments))
    for comment in comments:
        print('\t', comment)
        print('\t\tpost:', comment.post)
        print('\t\tauthor:', comment.author)


if __name__ == '__main__':
    reload_database()  # deletes and creates again the database
    query_database()  # runs a few queries on the created database
