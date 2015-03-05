"""Test data storage object."""

from tests.subscriber_server.unittest import TestCase

# pylint: disable=R0903
class TestDataStorage(TestCase):
    """Test persistent data storage."""

    def test_rw(self):
        """Read/Write."""
