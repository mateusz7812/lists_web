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

        self.browser.get("http://localhost:5000/user/logout")

        self.assertEqual(None, self.browser.get_cookie("user_id"))
        self.assertEqual(None, self.browser.get_cookie("user_key"))

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
                        "user_id": user_id},
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
                        "user_id": user_id},
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
        self.browser.delete_all_cookies()

        self.browser.add_cookie({"name": "user_id", "value": str(user_id)})
        self.browser.add_cookie({"name": 'user_key', "value": user_key})

        self.browser.get("http://localhost:5000/list/"+str(list_id))

        list_name_field = self.browser.find_element_by_id('list_name')
        list_content_field = self.browser.find_element_by_id('list_content')

        self.assertEqual("test", list_name_field.text)
        self.assertEqual("test", list_content_field.text)

        list_name_field = self.browser.find_element_by_name('name')
        list_name_field.send_keys("test")

        button = self.browser.find_element_by_id('del_list_btn')
        button.click()

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "list",
                        "user_id": user_id},
             "action": "get"})

        time.sleep(2)

        self.assertEqual(0, len(response["objects"]))

    def test_log_out_btn(self):
        self.browser.get("http://localhost:5000")
        self.browser.delete_all_cookies()

        self.browser.get("http://localhost:5000/user/login")

        self.assertEqual(0, len(self.browser.find_elements_by_id('log_out_btn')))

        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "other1"},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "other1",
                        "login": "other1",
                        "password": "other1"},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "login": "other1",
                        "password": "other1"},
             "action": "get"})

        user_id = response["objects"][0]["id"]

        requester.make_request(
            {"account": {"type": "account",
                         "login": "other1",
                         "password": "other1"},
             "object": {"type": "session",
                        "user_id": user_id},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "other1",
                         "password": "other1"},
             "object": {"type": "session",
                        "user_id": user_id},
             "action": "get"})

        user_key = response["objects"][0]["key"]

        self.browser.add_cookie({"name": "user_id", "value": str(user_id)})
        self.browser.add_cookie({"name": 'user_key', "value": user_key})

        self.browser.get("http://localhost:5000/list")

        self.assertEqual(1, len(self.browser.find_elements_by_id('log_out_btn')))

    def test_search_results(self):
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "other1"},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "other1",
                        "login": "other1",
                        "password": "other1"},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "login": "other1",
                        "password": "other1"},
             "action": "get"})

        other1_id = response["objects"][0]["id"]

        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "other2"},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "other2",
                        "login": "other2",
                        "password": "other2"},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "login": "other2",
                        "password": "other2"},
             "action": "get"})

        other2_id = response["objects"][0]["id"]

        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "list",
                        "name": "other3"},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "account",
                         "login": "other1",
                         "password": "other1"},
             "object": {"type": "list",
                        "user_id": other1_id,
                        "name": "other3",
                        "content": "other3"},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "other1",
                         "password": "other1"},
             "object": {"type": "list",
                        "user_id": other1_id,
                        "name": "other3",
                        "content": "other3"},
             "action": "get"})

        other3_id = response["objects"][0]["id"]

        requester.make_request(
            {"account": {"type": "account",
                         "login": "other1",
                         "password": "other1"},
             "object": {"type": "session",
                        "user_id": other1_id},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "other1",
                         "password": "other1"},
             "object": {"type": "session",
                        "user_id": other1_id},
             "action": "get"})

        user_key = response["objects"][0]["key"]

        self.browser.get("http://localhost:5000")
        self.browser.delete_all_cookies()

        self.browser.add_cookie({"name": "user_id", "value": str(other1_id)})
        self.browser.add_cookie({"name": 'user_key', "value": user_key})

        self.browser.get("http://localhost:5000/search?query=other2")

        time.sleep(2)

        results = self.browser.find_elements_by_class_name("result")
        results[0].click()

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/user/' + str(other2_id))

        self.browser.get("http://localhost:5000/search?query=other3")

        time.sleep(2)

        results = self.browser.find_elements_by_class_name("result")
        results[0].click()

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list/' + str(other3_id))
