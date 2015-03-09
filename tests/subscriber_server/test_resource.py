"""test web resource."""

from twisted.python import components
from tests.subscriber_server.unittest import TestCase
from twisted.web.test.test_web import DummyRequest

from subscriber_server.server import SubscriberResource 
from subscriber_server import db

class TestWebResource(TestCase):
    """Test web server interface."""

    def test_ok_get(self):
        """Test resource 'GET' with no errors."""