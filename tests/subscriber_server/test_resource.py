# -*- coding: utf8 -*-
"""test web resource."""

import urllib

import mock
from zope.interface import implements
from twisted.python import components
from tests.subscriber_server.unittest import TestCase
from twisted.web.test.test_web import DummyRequest
from twisted.internet.defer import (
    inlineCallbacks,
    maybeDeferred,
)

from subscriber_server.server import SubscriberResource
from subscriber_server import db


class IDbMock(mock.Mock):
    """Mock of the db interface."""
    implements(db.IDatabase)

class TestWebResource(TestCase):
    """Test web server interface."""

    @inlineCallbacks
    def test_get_not_subscribed(self):
        """Test resource 'GET' with no errors."""
        uname = "no_user"
        topic = u"你好世界"
        self.db.retreiveMessage.side_effect = db.NotSubscribed(uname)
        (httpCode, _) = yield self.callNewMessage(topic, uname)
        self.assertEqual(httpCode, 404)
        self.db.retreiveMessage.assert_called_with(topic=topic, user=uname)

    @inlineCallbacks
    def test_get_no_messages_in_queue(self):
        """Test resource 'GET' with no errors."""
        uname = "no_user"
        topic = u"你好世界"
        self.db.retreiveMessage.side_effect = db.EmptyMessageQueue(uname)
        (httpCode, _) = yield self.callNewMessage(topic, uname)
        self.assertEqual(httpCode, 204)
        self.db.retreiveMessage.assert_called_with(topic=topic, user=uname)

    @inlineCallbacks
    def test_get_ok(self):
        """Test resource 'GET' with no errors."""
        uname = "no_user"
        topic = u"你好世界"
        message = "Sperm Whale and Bowl of Petunias"
        self.db.retreiveMessage.return_value = message
        (httpCode, response) = yield self.callNewMessage(topic, uname)
        self.assertEqual(httpCode, 200)
        self.assertEqual(response, message)
        self.db.retreiveMessage.assert_called_with(topic=topic, user=uname)

    @inlineCallbacks
    def test_subscribe(self):
        """Test 'subscribe' operation."""
        uname = "cat"
        topic = u"Schrödinger"
        (httpCode, _) = yield self.callSubscribe(topic, uname)
        self.assertEqual(httpCode, 200)
        self.db.subscribe.assert_called_with(topic=topic, user=uname)

    @inlineCallbacks
    def test_unsubscribe_ok(self):
        """Test 'unsubscribe' that reports no error."""
        uname = "cat"
        topic = u"Schrödinger"
        (httpCode, _) = yield self.callUnsubscribe(topic, uname)
        self.assertEqual(httpCode, 200)
        self.db.unsubscribe.assert_called_with(topic=topic, user=uname)

    @inlineCallbacks
    def test_unsubscribe_not_subscribed(self):
        """Test 'unsubscribe' that reports 'not subscribed' error."""
        uname = "cat"
        topic = u"Schrödinger"
        self.db.unsubscribe.side_effect = db.NotSubscribed(uname)
        (httpCode, _) = yield self.callUnsubscribe(topic, uname)
        self.assertEqual(httpCode, 404)
        self.db.unsubscribe.assert_called_with(topic=topic, user=uname)

    @inlineCallbacks
    def test_publish(self):
        """Test 'publish' op."""
        topic = u"Schrödinger"
        text = u"""
            Las Cabeceras HTTP son los parámetros que se envían en una petición o respuesta HTTP al cliente o al servidor para proporcionar
            información esencial sobre la transacción en curso. Estas cabeceras proporcionan información mediante la sintaxis 'Cabecera: Valor'
            y son enviadas automáticamente por el navegador o el servidor Web.
        """
        (httpCode, _) = yield self.callPublish(topic, text)
        self.assertEqual(httpCode, 200)
        self.db.publishMessage.assert_called_with(topic=topic, message=text)


    def setUp(self):
        self.db = IDbMock(db.IDatabase.names())
        self.view = SubscriberResource(self.db)

    def callNewMessage(self, topic, username):
        """Helper method that simulates/executes `GET /<topic>/<username>` retuest.

            Returns: Deferred that will resolve to the response of the view
        """
        return self._mkTestResponse(self._mkRequest([topic, username], "GET"))

    def callSubscribe(self, topic, username):
        """Helper method to call "subscribe" function of the HTTP server."""
        return self._mkTestResponse(self._mkRequest([topic, username], "POST"))

    def callPublish(self, topic, payload):
        """Fake 'publish' request."""
        return self._mkTestResponse(self._mkRequest([topic], "POST", args={
            "payload": [payload.encode("utf8")],
        }))

    def callUnsubscribe(self, topic, username):
        """Fake 'unsubscribe' request."""
        return self._mkTestResponse(self._mkRequest([topic, username], "DELETE"))

    def _mkRequest(self, path, method="GET", args=None):
        """Create dummy request mathing the spec."""
        postpath = tuple(path)
        postpath = [el.encode("utf8") for el in postpath]
        url = urllib.quote("/" + ("/".join(postpath)))
        request = DummyRequest(postpath)
        request.path = url
        request.uri = url # No need to think about GET arguments - we don't support any
        request.method = method
        if args:
            request.args = dict(args)
        return request

    def _mkTestResponse(self, request):
        """Returns a deferred that call backs with (http_code, response_text).

        Useful testing shorthand.
        """
        responseD = maybeDeferred(self.view.render, request)
        responseD.addCallback(lambda response: (request.responseCode, response))
        return responseD
