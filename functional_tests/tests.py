import time
from unittest import TestCase
from selenium import webdriver


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
        self.assertRegex(current_url, '/user/')

        button = self.browser.find_element_by_id('register')
        button.click()

        time.sleep(5)

        # register page

        current_url = self.browser.current_url
        self.assertRegex(current_url, '/user/register/')

        nick_input_box = self.browser.find_element_by_id('nick')
        login_input_box = self.browser.find_element_by_id('login')
        password_input_box = self.browser.find_element_by_id('password')

        nick_input_box.send_keys('test')
        login_input_box.send_keys('test')
        password_input_box.send_keys('test')

        button = self.browser.find_element_by_tag_name('submit')
        button.click()

        time.sleep(5)

        # login page

        current_url = self.browser.current_url
        self.assertEqual(current_url, '/user/login/')

        login_input_box = self.browser.find_element_by_id('login')
        password_input_box = self.browser.find_element_by_id('password')

        login_input_box.send_keys('test')
        password_input_box.send_keys('test')

        button = self.browser.find_element_by_tag_name('submit')
        button.click()

        time.sleep(5)

        user_id = self.browser.get_cookie("user_id")
        user_key = self.browser.get_cookie("user_key")

        self.assertEqual(int, type(user_id))
        self.assertEqual(str, type(user_key))

        # main page

        current_url = self.browser.current_url
        self.assertEqual(current_url, '/')

        button = self.browser.find_element_by_id('lists_btn')
        button.click()

        # lists page

        current_url = self.browser.current_url
        self.assertEqual(current_url, '/lists/')

        lists = self.browser.find_elements_by_class_name("list")
        self.assertEqual(0, len(lists))

        button = self.browser.find_element_by_id('add_list_btn')
        button.click()

        time.sleep(5)

        # adding list

        name_input_box = self.browser.find_element_by_id('name')
        content_input_box = self.browser.find_element_by_id('content')

        name_input_box.send_keys('neme')
        content_input_box.send_keys('content')

        button = self.browser.find_element_by_tag_name('submit')
        button.click()

        time.sleep(5)

        # added list check

        current_url = self.browser.current_url
        self.assertEqual(current_url, '/list/')

        lists = self.browser.find_elements_by_class_name("list")
        self.assertEqual(1, len(lists))

        lists[0].click()
        time.sleep(5)

        current_url = self.browser.current_url
        self.assertNotEqual(len(current_url), len('/list/'))

        # deleting list

        button = self.browser.find_element_by_id('del_list_btn')
        button.click()

        time.sleep(5)

        # check list deleting

        current_url = self.browser.current_url
        self.assertEqual(current_url, '/list/')

        lists = self.browser.find_elements_by_class_name("list")
        self.assertEqual(0, len(lists))

        # logging out user

        button = self.browser.find_element_by_id('log_out_btn')
        button.click()

        time.sleep(5)

        current_url = self.browser.current_url
        self.assertEqual(current_url, '/user/')



