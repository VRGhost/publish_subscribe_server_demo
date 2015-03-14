"""The core methods that run the whole application.

The main entry function is named `main`.
"""

import argparse

from twisted.web import server
from twisted.internet import reactor

import subscriber_server.db
import subscriber_server.server

def get_arg_parser():
    """Return ArgumentParser object for this program."""
    parser = argparse.ArgumentParser(description="Publish/subscribe server")
    parser.add_argument("--port", help="Port to bind to", type=int, default=5000)
    parser.add_argument(
        "--db",
        help="File to the database to use for message persistence.",
        default="./publish_subscribe.db",
    )
    return parser


def main(args):
    """Main entry method."""
    db = subscriber_server.db.DatabaseImpl(args.db)
    webResource = subscriber_server.server.SubscriberResource(db)
    site = server.Site(webResource)
    reactor.listenTCP(args.port, site)

    print "Starting the Publish/Subscribe server at the port {} (using database {!r})".format(
        args.port, args.db)

    db.open()
    try:
        reactor.run()
    finally:
        db.shutdown()
