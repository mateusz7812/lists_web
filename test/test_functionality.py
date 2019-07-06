import time
from unittest import TestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

import Main
from requester import Requester

requester = Requester()


class TestWeb(TestCase):
    def setUp(self):
        Main.run()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        Main.terminate()
        self.browser.quit()

    def test_basic_sequence(self):
        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "account",
                        "login": "test"},
             "action": "del"})

        self.browser.get("http://localhost")

        # user page

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/user/login')

        button = self.browser.find_element_by_id('register')
        button.click()

        # register page

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/user/register')

        nick_input_box = self.browser.find_element_by_name('nick')
        login_input_box = self.browser.find_element_by_name('login')
        password_input_box = self.browser.find_element_by_name('password')
        email_input_box = self.browser.find_element_by_name('email')

        nick_input_box.send_keys('test')
        login_input_box.send_keys('test')
        password_input_box.send_keys('test')
        email_input_box.send_keys('email@gmail.com')
        password_input_box.send_keys(Keys.ENTER)

        # login page

        time.sleep(2)

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/user/login')

        login_input_box = self.browser.find_element_by_name('login')
        password_input_box = self.browser.find_element_by_name('password')

        login_input_box.send_keys('test')
        password_input_box.send_keys('test')
        password_input_box.send_keys(Keys.ENTER)

        time.sleep(4)

        user_id = int(self.browser.get_cookie("user_id")["value"])
        user_key = self.browser.get_cookie("user_key")["value"]

        self.assertEqual(int, type(user_id))
        self.assertEqual(str, type(user_key))

        time.sleep(2)

        # lists page

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list')

        requester.make_request(
            {"account": {"type": "admin", "login": "admin", "password": "admin"},
             "object": {"type": "list",
                        "user_id": user_id},
             "action": "del"})
        self.browser.refresh()

        lists = self.browser.find_elements_by_class_name("list")
        self.assertEqual(0, len(lists))

        button = self.browser.find_element_by_id('add_list_div')
        button.click()

        # adding list

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list/add')

        name_input_box = self.browser.find_element_by_name('name')
        content_input_box = self.browser.find_element_by_name('content')

        name_input_box.send_keys('name')
        content_input_box.send_keys('content')
        name_input_box.send_keys(Keys.ENTER)

        # added list check

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list')

        lists = self.browser.find_elements_by_class_name("list-small")
        self.assertEqual(1, len(lists))

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "list",
                        "user_id": user_id},
             "action": "get"})

        list_id = response["objects"][0]["id"]

        lists[0].click()

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list/' + str(list_id))

        # deleting list

        self.browser.find_element_by_id('del_form_shower').click()
        name_input_box = self.browser.find_element_by_name('name')
        name_input_box.send_keys("name")

        button = self.browser.find_element_by_id('del_list_btn')
        button.click()

        # check list deleting

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list')

        lists = self.browser.find_elements_by_class_name("list")
        self.assertEqual(0, len(lists))

        # logging out user

        button = self.browser.find_element_by_id('log_out_div')
        button.click()

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/user')

    def test_followers_sequence(self):
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
                        "login": "test",
                        "password": "test"},
             "action": "get"})

        test_id = response["objects"][0]["id"]

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
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "follow",
                        "followed": other1_id,
                        "follower": test_id,
                        "following": "follow_account"},
             "action": "del"})

        self.browser.get("http://localhost")

        login_input_box = self.browser.find_element_by_name('login')
        password_input_box = self.browser.find_element_by_name('password')

        login_input_box.send_keys('test')
        password_input_box.send_keys('test')
        password_input_box.send_keys(Keys.ENTER)

        time.sleep(4)

        search_bar = self.browser.find_element_by_id("search_bar")

        search_bar.send_keys("other1")
        search_bar.send_keys(Keys.ENTER)

        time.sleep(3)

        current_url = self.browser.current_url
        self.assertEqual(current_url[-20:], '/search?query=other1')

        results = self.browser.find_elements_by_class_name("result")
        results[0].click()

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/user/' + str(other1_id))

        follow_btn = self.browser.find_element_by_id("follow_btn")
        follow_btn.click()

        time.sleep(3)

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "follow",
                        "followed": other1_id,
                        "follower": test_id,
                        "following": "follow_account"},
             "action": "get"})

        self.assertEqual(1, len(response["objects"]))

        follow_btn = self.browser.find_element_by_id("follow_btn")
        follow_btn.click()

        time.sleep(3)

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "follow",
                        "followed": other1_id,
                        "follower": test_id,
                        "following": "follow_account"},
             "action": "get"})

        self.assertEqual(0, len(response["objects"]))

    def test_groups_sequence(self):
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
                        "login": "test",
                        "password": "test"},
             "action": "get"})

        test_id = response["objects"][0]["id"]

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
             "object": {"type": "group",
                        "name": "group_test"},
             "action": "del"})

        self.browser.get("http://localhost")

        login_input_box = self.browser.find_element_by_name('login')
        password_input_box = self.browser.find_element_by_name('password')

        login_input_box.send_keys('test')
        password_input_box.send_keys('test')
        password_input_box.send_keys(Keys.ENTER)

        time.sleep(2)

        groups_btn = self.browser.find_element_by_id("groups_div")
        groups_btn.click()

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/group')

        name_input_box = self.browser.find_element_by_name('new_group_name')
        name_input_box.send_keys('group_test')
        name_input_box.send_keys(Keys.ENTER)

        group_div = self.browser.find_element_by_xpath("//*[contains(text(),'group_test')]")
        group_div.click()

        time.sleep(2)

        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "group",
                        "name": "group_test"},
             "action": "get"})

        group_id = response['objects'][0]["id"]

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/group/' + str(group_id))

        header = self.browser.find_element_by_tag_name("h1")
        self.assertEqual("group_test", header.text)

        lists = self.browser.find_elements_by_class_name("list-small")
        self.assertEqual(0, len(lists))

        new_list_btn = self.browser.find_element_by_id("add_list_div")
        new_list_btn.click()

        name_input_box = self.browser.find_element_by_name('name')
        content_input_box = self.browser.find_element_by_name('content')
        visibility_select = Select(self.browser.find_element_by_name('visibility'))

        name_input_box.send_keys('name')
        content_input_box.send_keys('content')
        visibility_select.select_by_visible_text("group_test")
        name_input_box.send_keys(Keys.ENTER)

        time.sleep(2)

        self.browser.get("http://localhost/group/" + str(group_id))

        lists = self.browser.find_elements_by_class_name("list-small")
        self.assertEqual(1, len(lists))
