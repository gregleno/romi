import unittest

from rominet.encoders import Encoders


class TestEncoders(unittest.TestCase):

    def test_1(self):
        """Test that no cp happens if we accelerate by half the max acceleration."""

        Encoders(None)
