import time
from unittest import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class TestWeb(TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_sequence(self):
        self.browser.get("http://localhost:5000")

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

        nick_input_box.send_keys('test')
        login_input_box.send_keys('test')
        password_input_box.send_keys('test')
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

        time.sleep(2)

        user_id = int(self.browser.get_cookie("user_id")["value"])
        user_key = self.browser.get_cookie("user_key")["value"]

        self.assertEqual(int, type(user_id))
        self.assertEqual(str, type(user_key))

        # lists page

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list')

        lists = self.browser.find_elements_by_class_name("list")
        self.assertEqual(0, len(lists))

        button = self.browser.find_element_by_id('add_list_btn')
        button.click()

        # adding list

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list/add')

        name_input_box = self.browser.find_element_by_id('name')
        content_input_box = self.browser.find_element_by_id('content')

        name_input_box.send_keys('neme')
        content_input_box.send_keys('content')
        content_input_box.send_keys(Keys.ENTER)

        # added list check

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list')

        lists = self.browser.find_elements_by_class_name("list")
        self.assertEqual(1, len(lists))

        lists[0].click()

        current_url = self.browser.current_url
        self.assertNotEqual(len(current_url), len('/list'))

        # deleting list

        button = self.browser.find_element_by_id('del_list_btn')
        button.click()

        # check list deleting

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/list')

        lists = self.browser.find_elements_by_class_name("list")
        self.assertEqual(0, len(lists))

        # logging out user

        button = self.browser.find_element_by_id('log_out_btn')
        button.click()

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/user')
