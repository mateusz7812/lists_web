import json
from unittest import TestCase
from unittest.mock import patch

from requester import Requester


def ret_val(*args, **kwargs):
    data = [args, kwargs]

    class Value:
        content = bytes(json.dumps(data), "utf-8")
        raw = data

    return Value


class TestRequester(TestCase):
    def setUp(self):
        self.requester = Requester()

    @patch('requests.post', side_effect=ret_val)
    def test_make_request(self, test_patch):
        value = self.requester.make_request("message")
        self.assertEqual(value[1], {'data': '"message"'})
