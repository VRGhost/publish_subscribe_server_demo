"""Twisted Web Resource."""


from twisted.web import server
from twisted.web.resource import Resource

import subscriber_server.db as DbModule


class SubscriberResource(Resource):
    """Web resource that implements subscriber server interface."""
    isLeaf = True

    def __init__(self, db):
        """Create subscriber resource.

        Arguments:
            `db` - object of the `subscriber_Server.db.IDatabase` interface.
        """
        Resource.__init__(self)
        self.db = DbModule.IDatabase(db)

    def render_GET(self, request):
        """Respond to a 'GET' request."""

        if len(request.postpath) != 2:
            return self._interfaceError(request, "You must provide two-element path: /<topic>/<username>")

        (topic, username) = (el.decode("utf8") for el in request.postpath)
        
        try:
            rv = self.db.retreiveMessage(user=username, topic=topic)
            request.setResponseCode(200)
        except DbModule.NotSubscribed:
            request.setResponseCode(404)
            rv = "The subscription does not exist."
        except DbModule.EmptyMessageQueue:
            request.setResponseCode(204)
            # Smart client might not get below string as 204 (No Content) code implies that there should be no content returned to the client.
            rv = "There are no messages available for this topic on this user." 

        request.setHeader("Content-Type", "Content-Type: text/html; charset=utf-8")
        return rv.encode("utf8")

    def render_POST(self, request):
        """Respond to a 'POST' message."""

        if len(request.postpath) not in (1, 2):
            return self._interfaceError(request, "You must provide (1): two-element path '/<topic>/<username>' to subscribe (2): '/<topic>' to post")

        path = [el.decode("utf8") for el in request.postpath]
        request.setResponseCode(200)
        if len(path) == 2:
            # Subscribe.
            (topic, uname) = path
            self.db.subscribe(user=uname, topic=topic)
            rv = "Subscription succeeded."
        elif len(path) == 1:
            # Post
            (topic, ) = path
            for payload in request.args["payload"]:
                payload = payload.decode("utf8")
                self.db.publishMessage(topic=topic, message=payload)
            rv = "Publish succeeded."
        return rv

    def render_DELETE(self, request):
        """Respond to a 'DELETE' message."""
        if len(request.postpath) != 2:
            return self._interfaceError(request, "You must provide two-element path: /<topic>/<username>")

        (topic, username) = (el.decode("utf8") for el in request.postpath)
        request.setHeader("Content-Type", "text/plain")
        try:
            self.db.unsubscribe(user=username, topic=topic)
            request.setResponseCode(200)
            rv = "OK"
        except DbModule.NotSubscribed:
            request.setResponseCode(404)
            rv = "The subscription does not exist."
        return rv

    def _interfaceError(self, request, message):
        """Handler that is executed when the request does not correspond to any of the interfaces declared in the Requirements."""
        # Returning HTTP error code 400 (Bad request) would be appropriate in this case.
        # But I've always wanted to see what the browser will do if the code 418 ("I'm a teapot"/RFC 2324) is returned
        request.setResponseCode(418) 
        request.setHeader("Content-Type", "text/plain")
        return message