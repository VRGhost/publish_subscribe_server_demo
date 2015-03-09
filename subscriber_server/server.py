"""Twisted Web Resource."""

from twisted.web.resource import Resource

class SubscriberResource(Resource):
    """Web resource that implements subscriber server interface."""
    isLeaf = True

    def __init__(self, db):
        super(SubscriberResource).__init__()
        self.db = db

    def render_GET(self, request):
        return "TEST"