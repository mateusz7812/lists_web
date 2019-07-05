from unittest.mock import MagicMock
from flask import Response
from flask_testing import TestCase
import app as ap


class LoginTest(TestCase):

    def create_app(self):
        app = ap.app
        app.config['TESTING'] = True
        app.secret_key = 'super secret key'
        app.config['SESSION_TYPE'] = 'filesystem'
        return app

    def test_index_redirecting_login_logout(self):
        user = {"id": 1, "nick": "test", "login": "test", "password": "test"}
        user_key = "abc"

        def make_request_mock(request):
            if request["object"]["type"] == "account":
                return {"objects": [user]}
            elif request["object"]["type"] == "session":
                return {"status": "handled", "objects": [{"key": user_key}]}
            return {"status": "handled", "objects": []}

        ap.requester.make_request = make_request_mock

        client = self.app.test_client()

        data: Response = client.get("/")
        self.assertRedirects(data, '/user/login')

        client.post("/user/login", data=dict(
            login='test',
            password='test'
        ), follow_redirects=True)

        cookies = {}
        for cookie in list(client.cookie_jar):
            cookies[cookie.name] = cookie.value

        self.assertEqual('1', cookies["user_id"])
        self.assertEqual('abc', cookies["user_key"])

        data = client.get("/user/logout")
        self.assertRedirects(data, '/')
        self.assertEqual(['user_id=', 'user_key='], [x.split(";")[0] for x in data.headers.get_all('Set-cookie')[:2]])

    def test_bad_login(self):
        def make_request_mock(_):
            return {"status": "handled", "objects": []}

        ap.requester.make_request = make_request_mock

        client = self.app.test_client()

        data: Response = client.get("/")
        self.assertRedirects(data, '/user/login')

        data = client.post("/user/login", data=dict(
            login='test',
            password='test'
        ), follow_redirects=True)

        info_p = data.data.find(b"account not found")
        self.assertNotEqual(-1, info_p)

    def test_list_adding(self):
        user = {"id": 1, "nick": "test", "login": "test", "password": "test"}
        user_key = "abc"

        def make_request_mock(request):
            if request["object"]["type"] == "account":
                return {"objects": [user]}
            elif request["object"]["type"] == "session":
                return {"status": "handled", "objects": [{"key": user_key}]}
            return {"status": "handled", "objects": []}

        ap.requester = MagicMock()
        ap.requester.make_request.side_effect = make_request_mock

        client = self.app.test_client()

        client.set_cookie("/", "user_id", str(user["id"]))
        client.set_cookie("/", "user_key", user_key)

        data = client.post("http://localhost/list/add", data=dict(
            name='test',
            content='test',
            visibility='none'
        ))

        self.assertRedirects(data, '/list')

        db_req_object = list(ap.requester.make_request.call_args)[0][0]["object"]
        self.assertEqual('list', db_req_object["type"])
        self.assertEqual(user["id"], db_req_object["user_id"])
        self.assertEqual('test', db_req_object["name"])
        self.assertEqual('test', db_req_object["content"])
        self.assertEqual('add', list(ap.requester.make_request.call_args)[0][0]["action"])

    def test_list_id_page(self):
        user = {"id": 1, "nick": "test", "login": "test", "password": "test"}
        user_key = "abc"
        a_list = {"id": 2, "user_id": 1, "name": "test", "content": "test", "date": "date"}

        def make_request_mock(request):
            if request["object"]["type"] == "account":
                return {"objects": [user]}
            elif request["object"]["type"] == "session":
                return {"status": "handled", "objects": [{"key": user_key}]}
            elif request["object"]["type"] == "list":
                return {"status": "handled", "objects": [a_list]}
            return {"status": "handled", "objects": []}

        ap.requester = MagicMock()
        ap.requester.make_request.side_effect = make_request_mock

        client = self.app.test_client()

        client.set_cookie("/", "user_id", str(user["id"]))
        client.set_cookie("/", "user_key", user_key)

        response = client.get("http://localhost/list/" + str(a_list["id"]))

        self.assertNotEqual(-1, response.data.find(b"test - test"))

        data = client.post("http://localhost/list/del", data=dict(
            name='test',
            id=2
        ))

        self.assertRedirects(data, '/')

        db_req_object = list(ap.requester.make_request.call_args)[0][0]["object"]
        self.assertEqual('list', db_req_object["type"])
        self.assertEqual(2, db_req_object["id"])
        self.assertEqual('test', db_req_object["name"])
        self.assertEqual('del', list(ap.requester.make_request.call_args)[0][0]["action"])

    def test_search_results(self):
        user1 = {"id": 1, "nick": "other1", "login": "other1", "password": "other1"}
        user2 = {"id": 2, "nick": "other2", "login": "other2", "password": "other2"}
        user_key = "abc"
        a_list = {"id": 2, "user_id": 1, "name": "test", "content": "test", "date": "date"}
        group = {"id": 10, "name": "test"}

        def make_request_mock(request):
            if request["object"]["type"] == "account":
                if "id" in request["object"]:
                    return {"objects": [user1]}
                if "login" in request["object"]:
                    if request["object"]["login"] == "other1":
                        return {"objects": [user1]}
                    elif request["object"]["login"] == "other2":
                        return {"objects": [user2]}
                if "nick" in request["object"]:
                    if request["object"]["nick"] == "other1":
                        return {"objects": [user1]}
                    elif request["object"]["nick"] == "other2":
                        return {"objects": [user2]}
            elif request["object"]["type"] == "session":
                return {"status": "handled", "objects": [{"key": user_key}]}
            elif request["object"]["type"] == "list":
                return {"status": "handled", "objects": [a_list]}
            elif request["object"]["type"] == "group":
                return {"status": "handled", "objects": [group]}
            return {"status": "handled", "objects": []}

        ap.requester = MagicMock()
        ap.requester.make_request.side_effect = make_request_mock

        client = self.app.test_client()

        client.set_cookie("/", "user_id", str(user1["id"]))
        client.set_cookie("/", "user_key", user_key)

        response = client.get("http://localhost/search?query=other2")

        self.assertNotEqual(-1, response.data.find(b"result"))
        self.assertNotEqual(-1, response.data.find(bytes('/user/' + str(user2["id"]), "utf-8")))

        client.get("http://localhost/search?query=other3")

        self.assertNotEqual(-1, response.data.find(b"result"))
        self.assertNotEqual(-1, response.data.find(bytes('/list/' + str(a_list["id"]), "utf-8")))

        requests = list(
            map(lambda x: x["object"]["type"],
                filter(lambda x: x["action"] == "get",
                       map(lambda x: x[1][0],
                           map(list,
                               list(ap.requester.method_calls))))))
        self.assertIn("group", requests)

    def test_followed_lists(self):
        user = {"id": 1, "nick": "test", "login": "test", "password": "test"}
        user1 = {"id": 2, "nick": "other1", "login": "other1", "password": "other1"}
        user2 = {"id": 3, "nick": "other2", "login": "other2", "password": "other2"}
        user_key = "abc"
        list1 = {"id": 4, "user_id": 2, "name": "other1_list", "content": "test", "date": "2010-2-2 02:02"}
        list2 = {"id": 5, "user_id": 3, "name": "other2_list", "content": "test", "date": "2010-2-3 03:02"}

        def make_request_mock(request):
            if request["object"]["type"] == "account":
                if "id" in request["object"]:
                    if request["object"]["id"] == 2:
                        return {"objects": [user1]}
                    elif request["object"]["id"] == 3:
                        return {"objects": [user2]}
                    elif request["object"]["id"] == 1:
                        return {"objects": [user]}
                if "login" in request["object"]:
                    if request["object"]["login"] == "other1":
                        return {"objects": [user1]}
                    elif request["object"]["login"] == "other2":
                        return {"objects": [user2]}
                    elif request["object"]["login"] == "test":
                        return {"objects": [user]}
                if "nick" in request["object"]:
                    if request["object"]["nick"] == "other1":
                        return {"objects": [user1]}
                    elif request["object"]["nick"] == "other2":
                        return {"objects": [user2]}
                    elif request["object"]["nick"] == "test":
                        return {"objects": [user]}
            elif request["object"]["type"] == "session":
                return {"status": "handled", "objects": [{"key": user_key}]}
            elif request["object"]["type"] == "list":
                if "user_id" in request["object"]:
                    if request["object"]["user_id"] == user1["id"]:
                        return {"status": "handled", "objects": [list1]}
                    elif request["object"]["user_id"] == user2["id"]:
                        return {"status": "handled", "objects": [list2]}
            elif request["object"]["type"] == "follow":
                return {"status": "handled", "objects": [{"followed": user1["id"]}, {"followed": user2["id"]}]}
            return {"status": "handled", "objects": []}

        ap.requester = MagicMock()
        ap.requester.make_request.side_effect = make_request_mock

        client = self.app.test_client()

        client.set_cookie("/", "user_id", str(user1["id"]))
        client.set_cookie("/", "user_key", user_key)

        response = client.get("http://localhost/list/followed")

        self.assertEqual(2, response.data.count(b"list-small"))
        self.assertNotEqual(-1, response.data.find(b"other1 - other1_list"))
        self.assertNotEqual(-1, response.data.find(b"other2 - other2_list"))

    def test_group_add_list(self):
        user = {"id": 1, "nick": "test", "login": "test", "password": "test"}
        user_key = "abc"
        group = {"id": 10, "name": "test"}
        a_list = {"id": 2, "user_id": 1, "name": "test", "content": "test", "date": "2010-2-3 03:02"}
        follow = []

        def make_request_mock(request):
            if request["object"]["type"] == "account":
                return {"objects": [user]}
            elif request["object"]["type"] == "session":
                return {"status": "handled", "objects": [{"key": user_key}]}
            elif request["object"]["type"] == "list":
                return {"status": "handled", "objects": [a_list]}
            elif request["object"]["type"] == "follow" and \
                    request["object"]["following"] == "follow_group":
                return {"status": "handled", "objects": follow}
            return {"status": "handled", "objects": []}

        ap.requester = MagicMock()
        ap.requester.make_request.side_effect = make_request_mock

        client = self.app.test_client()

        client.set_cookie("/", "user_id", str(user["id"]))
        client.set_cookie("/", "user_key", user_key)

        response = client.get("http://localhost/list/followed")

        self.assertEqual(-1, response.data.find(b"list-small"))

        follow = [{"follower": user["id"], "followed": group["id"]}]

        response = client.get("http://localhost/list/followed")

        self.assertNotEqual(-1, response.data.find(b"list-small"))
