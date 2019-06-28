import time
from unittest import TestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import Main
from requester import Requester

requester = Requester()


class LoginTest(TestCase):
    def setUpClass():
        requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "admin",
                        "login": "admin",
                        "password": "admin",
                        "account_type": "admin"},
             "action": "add"})

    def setUp(self):
        Main.run()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        Main.terminate()
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

        self.browser.get("http://localhost/user/login")

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

        self.browser.get("http://localhost/user/logout")

        self.assertEqual(None, self.browser.get_cookie("user_id"))
        self.assertEqual(None, self.browser.get_cookie("user_key"))

    def test_bad_login(self):
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "test"},
             "action": "del"})

        self.browser.get("http://localhost/user/login")

        login_input_box = self.browser.find_element_by_name('login')
        password_input_box = self.browser.find_element_by_name('password')

        login_input_box.send_keys('test')
        password_input_box.send_keys('test')
        password_input_box.send_keys(Keys.ENTER)

        time.sleep(2)

        info_p = self.browser.find_element_by_id('info').text

        self.assertEqual("account not found", info_p)

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

        self.browser.get("http://localhost")

        self.browser.add_cookie({"name": "user_id", "value": str(user_id)})
        self.browser.add_cookie({"name": 'user_key', "value": user_key})

        self.browser.get("http://localhost/list/add")

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

        self.browser.get("http://localhost")
        self.browser.delete_all_cookies()

        self.browser.add_cookie({"name": "user_id", "value": str(user_id)})
        self.browser.add_cookie({"name": 'user_key', "value": user_key})

        self.browser.get("http://localhost/list/" + str(list_id))

        list_name_field = self.browser.find_element_by_id('list_name')
        list_content_field = self.browser.find_element_by_id('list_content')

        self.assertEqual("test - test", list_name_field.text)
        self.assertEqual("test", list_content_field.text)
        self.browser.find_element_by_id('del_form_shower').click()
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
        self.browser.get("http://localhost")
        self.browser.delete_all_cookies()

        self.browser.get("http://localhost/user/login")

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

        self.browser.get("http://localhost/list")

        self.assertEqual(1, len(self.browser.find_elements_by_id('log_out_div')))

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

        self.browser.get("http://localhost")
        self.browser.delete_all_cookies()

        self.browser.add_cookie({"name": "user_id", "value": str(other1_id)})
        self.browser.add_cookie({"name": 'user_key', "value": user_key})

        self.browser.get("http://localhost/search?query=other2")

        time.sleep(2)

        results = self.browser.find_elements_by_class_name("result")
        results[0].click()

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/user/' + str(other2_id))

        self.browser.get("http://localhost/search?query=other3")

        time.sleep(2)

        results = self.browser.find_elements_by_class_name("result")
        results[0].click()

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list/' + str(other3_id))

    def test_followeds_lists(self):
        # del old accounts
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "test"},
             "action": "del"})
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "other1"},
             "action": "del"})
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "other2"},
             "action": "del"})

        # del old lists
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "list",
                        "name": "other1_list"},
             "action": "del"})
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "list",
                        "name": "other2_list"},
             "action": "del"})

        # add accounts
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
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": "test",
                        "login": "test",
                        "password": "test"},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "login": "test",
                        "password": "test"},
             "action": "get"})

        test_id = response["objects"][0]["id"]

        # add lists

        requester.make_request(
            {"account": {"type": "account",
                         "login": "other1",
                         "password": "other1"},
             "object": {"type": "list",
                        "user_id": other1_id,
                        "name": "other1_list",
                        "content": "other_other_other_other_other_other_other"},
             "action": "add"})

        requester.make_request(
            {"account": {"type": "account",
                         "login": "other2",
                         "password": "other2"},
             "object": {"type": "list",
                        "user_id": other2_id,
                        "name": "other2_list",
                        "content": "other_other_other_other_other_other_other"},
             "action": "add"})

        # del old follows

        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "follow",
                        "follower": test_id},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "follow",
                        "followed": other1_id},
             "action": "del"})

        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "follow",
                        "followed": other2_id},
             "action": "del"})

        # set following

        requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "follow",
                        "followed": other1_id,
                        "follower": test_id},
             "action": "add"})

        requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "follow",
                        "followed": other2_id,
                        "follower": test_id},
             "action": "add"})

        # login test user

        requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "session",
                        "user_id": test_id},
             "action": "add"})

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "other1",
                         "password": "other1"},
             "object": {"type": "session",
                        "user_id": test_id},
             "action": "get"})

        test_key = response["objects"][0]["key"]

        self.browser.get("http://localhost")
        self.browser.delete_all_cookies()

        self.browser.add_cookie({"name": "user_id", "value": str(test_id)})
        self.browser.add_cookie({"name": 'user_key', "value": test_key})

        # check results

        self.browser.get("http://localhost/list/followed")

        results = self.browser.find_elements_by_class_name("list-small")
        self.assertEqual("other1 - other1_list", results[0].find_elements_by_tag_name("p")[0].text)
        self.assertEqual("other2 - other2_list", results[1].find_elements_by_tag_name("p")[0].text)
