import os
import sys
import random
import datetime
import requests
from flaskblog import db, bcrypt
from flaskblog.models import User, Post, Comment
from lorem_text import lorem

host = 'localhost'  # host where the system is running
port = 5000  # port where the process is running


def reload_database():
    try:
        response = requests.get(f'http://{host}:{port}')
        print('The website seems to be running. Please stop it and run this file again.', file=sys.stderr)
        exit(11)
    except Exception as e:
        pass
    try:
        os.remove('flaskblog/site.db')
        print('previous DB file removed')
    except:
        print('no previous file found')

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
    except:
        db.session.rollback()
        print('Error committing the users', file=sys.stderr)

    # testing if the users were added correctly
    assert len(User.query.all()) == 3, 'It seems that user failed to be inserted!'

    users = [default_user1, default_user2, default_user3]

    # creating posts for each user
    for user in [default_user1, default_user2]:

        # creating 3 to 6 posts
        for p in range(random.randint(3, 6)):

            # picking a random date for the post
            date_post = datetime.datetime.now() - \
                        datetime.timedelta(days=random.randint(1, 90),
                                           hours=random.randint(1, 23),
                                           minutes=random.randint(1, 59))

            post = Post(title=lorem.words(random.randint(3, 7)),
                        content_type='markdown',
                        content=lorem.paragraphs(random.randint(1, 3)),
                        date_posted=date_post,
                        author=user)

            db.session.add(post)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                print('Error committing the posts', file=sys.stderr)

            # for each post, creating 2 to 5 comments
            for c in range(random.randint(2, 5)):

                # picking a random date for the comment between the date of the post and now
                # get the difference between the date of the post and now
                diff = datetime.datetime.now() - date_post
                # compute the date of the comment using a random number from 1 to the number of seconds of the diff
                date_comment = datetime.datetime.now() - datetime.timedelta(seconds=random.randint(1, diff.seconds))

                # creating a new comment object
                comment = Comment(author=random.choice(users),  # selects a random user for the comment
                                  content=lorem.words(random.randint(10, 15)),
                                  date_posted=date_comment,
                                  post=post)

                # adding the comment object to the database
                db.session.add(comment)

            try:
                db.session.commit()
            except:
                db.session.rollback()
                print('Error committing the comments', file=sys.stderr)
            # testing if the comments were inserted correctly
            assert len(Comment.query.filter_by(post_id=post.id).all()) > 0, \
                f'The comments for post {post.id} were not successful!'

        # testing if the posts were inserted
        assert len(Post.query.filter_by(user_id=user.id).all()) > 0, 'Posts were not added correctly!'

    try:
        db.session.commit()
        print('\nFinalized - database created successfully!',  u'\u2713')
    except Exception as e:
        print('The operations were not successful. Error:', file=sys.stderr)
        print(e, file=sys.stderr)
        db.session.rollback()


def query_database():
    pass


if __name__ == '__main__':
    reload_database()
