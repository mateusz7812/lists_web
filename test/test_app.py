import time
from unittest import TestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import main
from requester import Requester

requester = Requester()


class LoginTest(TestCase):
    def setUp(self):
        main.run()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        main.terminate()
        self.browser.quit()

    def test_basic_login(self):
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "test"},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "test",
                        "login": "test",
                        "password": "test"},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "test",
                        "login": "test",
                        "password": "test"},
             "action": "get"})

        user_id = response["objects"][0]["id"]

        requester.make_request(
            {"account": {"type": "account",
                         "nick": "test",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "session",
                        "user_id": user_id},
             "action": "del"})

        self.browser.get("http://localhost:5000/user/login")

        login_input_box = self.browser.find_element_by_name('login')
        password_input_box = self.browser.find_element_by_name('password')

        login_input_box.send_keys('test')
        password_input_box.send_keys('test')
        password_input_box.send_keys(Keys.ENTER)

        time.sleep(2)

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "session",
                        "user_id": user_id},
             "action": "get"})

        user_key = response["objects"][0]["key"]

        time.sleep(1)

        self.assertEqual(user_id, int(self.browser.get_cookie("user_id")["value"]))
        self.assertEqual(user_key, self.browser.get_cookie("user_key")["value"])

    def test_list_adding(self):
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "test"},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "test",
                        "login": "test",
                        "password": "test"},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "test",
                        "login": "test",
                        "password": "test"},
             "action": "get"})

        user_id = response["objects"][0]["id"]

        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "list",
                        "user_id": user_id,
                        "name": "test"},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "session",
                        "user_id": user_id},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "session",
                        "user_id": user_id},
             "action": "get"})

        user_key = response["objects"][0]["key"]

        self.browser.get("http://localhost:5000")

        self.browser.add_cookie({"name": "user_id", "value": str(user_id)})
        self.browser.add_cookie({"name": 'user_key', "value": user_key})

        self.browser.get("http://localhost:5000/list/add")

        name_input_box = self.browser.find_element_by_name('name')
        content_input_box = self.browser.find_element_by_name('content')

        name_input_box.send_keys('test')
        content_input_box.send_keys('test')
        name_input_box.send_keys(Keys.ENTER)

        time.sleep(2)

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "list",
                        "user_id": user_id},
             "action": "get"})

        self.assertEqual("test", response["objects"][0]["name"])
        self.assertEqual("test", response["objects"][0]["content"])

    def test_list_id_page(self):
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "test"},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "test",
                        "login": "test",
                        "password": "test"},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "test",
                        "login": "test",
                        "password": "test"},
             "action": "get"})

        user_id = response["objects"][0]["id"]

        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "list",
                        "user_id": user_id,
                        "name": "test"},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "session",
                        "user_id": user_id},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "session",
                        "user_id": user_id},
             "action": "get"})

        user_key = response["objects"][0]["key"]

        requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "list",
                        "user_id": user_id,
                        "name": "test",
                        "content": "test"},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "list",
                        "user_id": user_id},
             "action": "get"})

        list_id = response["objects"][0]["id"]

        self.browser.get("http://localhost:5000")

        self.browser.add_cookie({"name": "user_id", "value": str(user_id)})
        self.browser.add_cookie({"name": 'user_key', "value": user_key})

        self.browser.get("http://localhost:5000/list/"+str(list_id))

        list_name_field = self.browser.find_element_by_id('list_name')
        list_content_field = self.browser.find_element_by_id('list_content')

        self.assertEqual("test", list_name_field.text)
        self.assertEqual("test", list_content_field.text)
