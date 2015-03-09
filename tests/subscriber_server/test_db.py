"""Test data storage object."""
import tempfile
import os

from tests.subscriber_server.unittest import TestCase
from subscriber_server import db as DB

from zope.interface.verify import verifyClass

class TestDataStorage(TestCase):
    """Test persistent data storage."""

    def test_interface(self):
        """Test DB implementation / interface match."""
        self.assertTrue(
            DB.IDatabase.implementedBy(DB.DatabaseImpl)
        )
        verifyClass(DB.IDatabase, DB.DatabaseImpl)


    def test_database_op_cycle(self):
        """Test DB register listener/publish message cycle."""
        user = "marvin"
        topic = "dead_beef"
        message = "hello, world"
        db = self._db

        db.subscribe(user, topic)
        db.publishMessage(topic, message)
        retMsg = db.retreiveMessage(user, topic)
        self.assertEqual(retMsg, message)
        # Mo more messages in the queue -> `EmptyMessageQueue` exception
        with self.assertRaises(DB.EmptyMessageQueue):
            db.retreiveMessage(user, topic)
        db.unsubscribe(user, topic)
        # Successive unsubscribe must raise `NotSubscribed` exception
        with self.assertRaises(DB.NotSubscribed):
            db.unsubscribe(user, topic)
        # Reading new messages for this topic should raise
        # `NotSubscribed` exception (even if there are messages in the topic)
        db.publishMessage(topic, message)
        with self.assertRaises(DB.NotSubscribed):
            db.retreiveMessage(user, topic)

    def test_many_messages_many_users(self):
        """Test that the database can handle multiple users per topic."""
        users = frozenset("user_{}".format(idx) for idx in xrange(10))
        topic = "test"
        messages = frozenset("message::{}".format(idx) for idx in xrange(10))
        db = self._db

        for user in users:
            db.subscribe(user, topic)
        for message in messages:
            db.publishMessage(topic, message)
        # check that each user is able to retreive all messages
        for user in users:
            thisUserMessages = set()
            try:
                while True:
                    thisUserMessages.add(db.retreiveMessage(user, topic))
            except DB.EmptyMessageQueue:
                # no more messages
                pass
            self.assertEqual(thisUserMessages, messages)

    def test_persistence(self):
        """Test that db can preserve its data over open/close cycle."""
        user = "marvin"
        topic = "dead_beef"
        message = "hello, world"
        db = self._db

        db.subscribe(user, topic)
        db.publishMessage(topic, message)

        db.shutdown()
        db.open()

        retMsg = db.retreiveMessage(user, topic)
        self.assertEqual(retMsg, message)

    def setUp(self):
        (handle, self.tmpDbFilename) = tempfile.mkstemp()
        os.close(handle)    # Close the file descriptor,
                            # file itself will be re-opened by the db object
        # Sadly, I have to delete the file here.
        # 'Shelve' hates empty (but existing) files
        os.unlink(self.tmpDbFilename)
        self._db = DB.DatabaseImpl(self.tmpDbFilename)
        self._db.open()

    def tearDown(self):
        self._db.shutdown()
        os.unlink(self.tmpDbFilename)

        