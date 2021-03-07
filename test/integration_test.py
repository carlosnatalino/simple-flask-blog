"""
Integration test for the system.

Before starting the test:

1. Run load_database.py
2. Run run.py
3. Check if the system is online.

The, we perform the following operations:
1 - Register
2 - Login
3 - Create a new post
4 - Edit a post
5 - Delete a post
6 - Logout
"""

import sys
import time
import random
import requests
from lorem_text import lorem
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

wait_time = 1  # number of minutes to wait between actions
host = 'localhost'  # host where the system is running
port = 5000  # port where the process is running


def test_setup():

    # checking if the system is online
    try:
        response = requests.get(f'http://{host}:{port}')
        if response.status_code != 200:
            print(f'The website returned status code {response.status_code}!', file=sys.stderr)
            print(f'Check if the site is correctly configured and running!', file=sys.stderr)
            exit(10)  # stop the execution of the text
    except Exception as e:
        print(f'We are having troubles connecting to the system!', file=sys.stderr)
        print(f'Check if the site is correctly configured and running!', file=sys.stderr)
        print(f'Error description: {e}')
        exit(11)

    # setup the browser
    global driver
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    # driver.maximize_window()  # maximize the window
    driver.get(f'http://{host}:{port}')
    time.sleep(wait_time)


def test_register():
    driver.find_element_by_id('register').click()
    time.sleep(wait_time)

    driver.find_element_by_id('username').send_keys('new_user')
    driver.find_element_by_id('email').send_keys('new@user.com')
    driver.find_element_by_id('password').send_keys('user_password')
    driver.find_element_by_id('confirm_password').send_keys('user_password')
    driver.find_element_by_id('submit').click()
    time.sleep(wait_time)

    # validate if a success message is displayed
    try:
        driver.find_element_by_class_name('alert-success')
    except NoSuchElementException as nsee:
        raise AssertionError('The registering process seems to have failed! Check/reload your database!')


def test_register_duplicate_user():
    driver.find_element_by_id('register').click()
    time.sleep(wait_time)

    # testing first the username unique constraint
    driver.find_element_by_id('username').send_keys('new_user')
    driver.find_element_by_id('email').send_keys('new2@user.com')
    driver.find_element_by_id('password').send_keys('user_password')
    driver.find_element_by_id('confirm_password').send_keys('user_password')
    driver.find_element_by_id('submit').click()
    time.sleep(wait_time)

    # verifying if message is correctly displayed
    assert 'This username is taken. Please choose a different one.' in driver.page_source

    # testing second the email unique constraint
    driver.find_element_by_id('username').clear()
    driver.find_element_by_id('username').send_keys('new_user2')
    driver.find_element_by_id('email').clear()
    driver.find_element_by_id('email').send_keys('new@user.com')
    driver.find_element_by_id('password').send_keys('user_password')
    driver.find_element_by_id('confirm_password').send_keys('user_password')
    driver.find_element_by_id('submit').click()
    time.sleep(wait_time)

    # verifying if message is correctly displayed
    assert 'This email is taken. Please choose a different one.' in driver.page_source


def test_login():
    driver.find_element_by_id('login').click()
    time.sleep(wait_time)
    driver.find_element_by_id('email').send_keys('new@user.com')
    driver.find_element_by_id('password').send_keys('user_password')
    driver.find_element_by_id('submit').click()
    time.sleep(wait_time)

    assert 'new-post' in driver.page_source


def test_new_post():
    driver.find_element_by_id('new-post').click()
    time.sleep(wait_time)

    driver.find_element_by_id('title').send_keys('This is a new post')
    driver.find_element_by_id('content_type-2').click()
    driver.find_element_by_id('content').send_keys('- This is the content of the new post.')
    driver.find_element_by_id('submit').click()
    time.sleep(wait_time)

    assert 'Your post has been created!' in driver.page_source


def test_edit_post():
    posts = driver.find_elements_by_tag_name('article')
    for post in posts:
        if 'new_user' in post.text:  # if the new_user is the author
            post.find_element_by_class_name('article-title').click()
            break
    time.sleep(wait_time)

    driver.find_element_by_id('update').click()
    time.sleep(wait_time)

    driver.find_element_by_id('title').clear()
    driver.find_element_by_id('title').send_keys('This is a updated post')
    driver.find_element_by_id('content_type-0').click()
    driver.find_element_by_id('content').send_keys('- This is the content of the new post.')
    driver.find_element_by_id('submit').click()
    time.sleep(wait_time)

    assert 'Your post has been updated!' in driver.page_source


def test_comment_post():
    posts = driver.find_elements_by_tag_name('article')
    post = random.choice(posts)
    post.find_element_by_class_name('article-title').click()
    time.sleep(wait_time)

    driver.find_element_by_id('content').send_keys(lorem.words(50))
    driver.find_element_by_id('submit').click()
    time.sleep(wait_time)

    assert 'Your comment has been created' in driver.page_source


def test_delete_post():
    driver.find_element_by_id('delete').click()
    time.sleep(wait_time)

    driver.find_element_by_id('confirm-delete').click()
    time.sleep(wait_time)

    assert 'Your post has been deleted!' in driver.page_source


def test_logout():
    driver.find_element_by_id('logout').click()
    time.sleep(wait_time)

    assert 'new-post' not in driver.page_source


def test_teardown():
    try:
        driver.quit()
    except:
        pass


if __name__ == '__main__':
    stop = False

    # this version shows the errors in the output
    test_setup()

    if stop:
        i = input('Setup ran correctly. Proceed? [Y/n]')
        if i.strip().lower() == 'n':
            exit(12)
    test_register()

    if stop:
        i = input('Register ran correctly. Proceed? [Y/n]')
        if i.strip().lower() == 'n':
            exit(12)
    test_register_duplicate_user()

    if stop:
        i = input('Test for duplicated users ran correctly. Proceed? [Y/n]')
        if i.strip().lower() == 'n':
            exit(12)
    test_login()

    if stop:
        i = input('Login ran correctly. Proceed? [Y/n]')
        if i.strip().lower() == 'n':
            exit(12)
    test_new_post()

    if stop:
        i = input('New post ran correctly. Proceed? [Y/n]')
        if i.strip().lower() == 'n':
            exit(12)
    test_edit_post()

    if stop:
        i = input('Edit post ran correctly. Proceed? [Y/n]')
        if i.strip().lower() == 'n':
            exit(12)
    test_delete_post()

    if stop:
        i = input('Delete post ran correctly. Proceed? [Y/n]')
        if i.strip().lower() == 'n':
            exit(12)
    test_comment_post()

    if stop:
        i = input('Comment on post ran correctly. Proceed? [Y/n]')
        if i.strip().lower() == 'n':
            exit(12)
    test_logout()

    if stop:
        i = input('Log out ran correctly. Proceed? [Y/n]')
        if i.strip().lower() == 'n':
            exit(12)
    test_teardown()

    # this version does not show the error
    # try:
    #     test_setup()
    #     # test_register()
    #     test_register_duplicate_user()
    #     test_login()
    #     test_new_post()
    #     test_edit_post()
    #     test_delete_post()
    #     test_logout()
    #     test_teardown()
    # except:
    #     print('An error happened during the test. Check the message below:')
    #     traceback.print_exc()
        # uncomment if you want the browser to close automatically when a failure happens
        # if driver is not None:  # closing the browser if an error happens
        #     test_teardown()
