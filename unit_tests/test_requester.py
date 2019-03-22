import json
from unittest import TestCase
from unittest.mock import patch

from requester import Requester


def retval(*args, **kargs):
    data = [args, kargs]

    class value:
        content = bytes(json.dumps(data), "utf-8")
        raw = data

    return value


class TestRequester(TestCase):
    def setUp(self):
        self.requester = Requester()

    @patch('requests.post', side_effect=retval)
    def test_make_request(self, test_patch):
        value = self.requester.make_request("message")
        self.assertEqual(value, [['http://localhost:8080'], {'data': '"message"'}])
