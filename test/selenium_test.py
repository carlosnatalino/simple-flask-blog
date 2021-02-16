'''
Test Script
1 - Register
2 - Login
3 - Create a new post
4 - Edit a post
5 - Delete a post
6 - Logout
'''

from flaskblog import app
from selenium import webdriver
from multiprocessing import Process
import time

wait_time = 1


def test_setup():
    # start flask application at background
    global server
    server = Process(target=app.run)
    server.start()

    # give the server a second to ensure it is up
    time.sleep(wait_time)

    # setup the browser
    global driver
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.maximize_window()
    driver.get("http://localhost:5000")
    time.sleep(wait_time)


def test_register():
    driver.find_element_by_id("register").click()
    time.sleep(wait_time)

    driver.find_element_by_id("username").send_keys("new_user")
    driver.find_element_by_id("email").send_keys("new@user.com")
    driver.find_element_by_id("password").send_keys("user_password")
    driver.find_element_by_id("confirm_password").send_keys("user_password")
    driver.find_element_by_id("submit").click()
    time.sleep(wait_time)

    assert "Your account has been created! You are now able to log in!" in driver.page_source


def test_login():
    driver.find_element_by_id("email").send_keys("new@user.com")
    driver.find_element_by_id("password").send_keys("user_password")
    driver.find_element_by_id("submit").click()
    time.sleep(wait_time)

    assert "new-post" in driver.page_source


def test_new_post():
    driver.find_element_by_id("new-post").click()
    time.sleep(wait_time)

    driver.find_element_by_id("title").send_keys("This is a new post")
    driver.find_element_by_id("content_type-2").click()
    driver.find_element_by_id("content").send_keys("- This is the content of the new post.")
    driver.find_element_by_id("submit").click()
    time.sleep(wait_time)

    assert "Your post has been created!" in driver.page_source


def test_edit_post():
    posts = driver.find_elements_by_class_name("article-title")
    for post in posts:
        if post.text == "This is a new post":
            post.click()
            break
    time.sleep(wait_time)

    driver.find_element_by_id("update").click()
    time.sleep(wait_time)

    driver.find_element_by_id("title").clear()
    driver.find_element_by_id("title").send_keys("This is a updated post")
    driver.find_element_by_id("content_type-0").click()
    driver.find_element_by_id("content").send_keys("- This is the content of the new post.")
    driver.find_element_by_id("submit").click()
    time.sleep(wait_time)

    assert "Your post has been updated!" in driver.page_source


def test_delete_post():
    driver.find_element_by_id("delete").click()
    time.sleep(wait_time)

    driver.find_element_by_id("confirm-delete").click()
    time.sleep(wait_time)

    assert "Your post has been deleted!" in driver.page_source


def test_logout():
    driver.find_element_by_id("logout").click()
    time.sleep(wait_time)

    assert "new-post" not in driver.page_source


def test_teardown():
    try:
        driver.quit()
    except:
        pass
    server.terminate()
    server.join()


if __name__ == '__main__':
    test_setup()
    test_register()
    test_teardown()