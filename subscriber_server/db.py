"""Database/Data persistence module."""

import contextlib
import os
import shelve
import threading

from zope.interface import (
    Interface,
    implements,
)

class DbError(Exception):
    """Base class for DB exceptions."""

class EmptyMessageQueue(DbError):
    """No messages in the messaging queue."""

class NotSubscribed(DbError):
    """User is not subscribed to the topic."""

# pylint: disable=E0213,E0211,E0239
class IDatabase(Interface):
    """Database interface."""

    def publishMessage(topic, message):
        """Publish a message into a topic."""

    def subscribe(user, topic):
        """Subscribe user to a topic."""

    def retreiveMessage(user, topic):
        """Retreive a message for a user for a topic.

        Returns:
            Message (string)
        Raises:
            EmptyMessageQueue, NotSubscribed
        """

    def unsubscribe(user, topic):
        """Unsubscribe user from a topic.

        Raises:
            NotSubscribed
        """

    def open():
        """Open connection to the database."""

    def shutdown():
        """Shut down connection to the database."""

class _DbTopic(object):
    """Internal db representation of the 'topic' object."""

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def addUser(self, user):
        """Add `user` (string) to a topic."""
        if user not in self.data:
            self.data[user] = []

    def removeUser(self, user):
        """Remove user from a topic."""
        try:
            del self.data[user]
        except KeyError:
            raise NotSubscribed(user)

    def getData(self):
        """Return data contained in the topic."""
        return self.data

    def publishMessage(self, message):
        for msgQueue in self.data.itervalues():
            msgQueue.append(message)

    def retreive(self, user):
        """Retreive a next message for the user."""
        try:
            userQueue = self.data[user]
        except KeyError:
            raise NotSubscribed(user)
        try:
            return userQueue.pop()
        except IndexError:
            raise EmptyMessageQueue(user)

    def __str__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.name)

class DatabaseImpl(object):
    """Real DB implementation."""

    implements(IDatabase)

    def __init__(self, fileName):
        """Initialise the database object.

        param: fileName, file name to open/create
        """
        self._targetFileName = fileName
        assert os.path.isdir(os.path.dirname(fileName)), fileName
        self._source = None
        self._excl = threading.Lock()

    def subscribe(self, user, topic):
        """Subscribe user to a topic."""
        with self._topic(topic) as topic:
            topic.addUser(user)

    def unsubscribe(self, user, topic):
        """Unsubscribe user from a topic."""
        with self._topic(topic) as topic:
            topic.removeUser(user)

    def publishMessage(self, topic, message):
        """Publsh message for a topic."""
        with self._topic(topic) as topic:
            topic.publishMessage(message)

    def retreiveMessage(self, user, topic):
        """Retreive message fror a user."""
        with self._topic(topic) as topic:
            return topic.retreive(user)

    def open(self):
        """Open Db."""
        with self._excl:
            if not self._source:
                self._source = shelve.open(self._targetFileName)

    def shutdown(self):
        """Shutdown DB."""
        with self._excl:
            if self._source:
                self._source.close()
                self._source = None

    @contextlib.contextmanager
    def _topic(self, name):
        """Topic context."""
        # Shelf DB does not accept unicode keys
        dbKey = name.encode("utf8")
        with self._excl:

            try:
                data = self._source[dbKey]
            except KeyError:
                data = {}

            topic = _DbTopic(name, data)
            try:
                yield topic
            finally:
                self._source[dbKey] = topic.getData()
