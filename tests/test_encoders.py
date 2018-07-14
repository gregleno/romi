import mock
import unittest

from rominet.a_star import AStar
from rominet.encoders import Encoders


class TestEncoders(unittest.TestCase):

    def test_read_encoders(self):
        astar = mock.MagicMock(spec=AStar)
        astar.read_encoders.side_effect = [(0, 0), (1, 1)]
        e = Encoders(astar)
        self.assertEqual((0, 0), e.read_encoders())
        self.assertEqual((1, 1), e.read_encoders())

    def test_overrun(self):
        astar = mock.MagicMock(spec=AStar)
        before = 0x10000 - 1
        astar.read_encoders.side_effect = [(before, before), (1, 1)]
        e = Encoders(astar)
        e.read_encoders()
        self.assertEqual((2, 2), e.read_encoders())

    def test_underrun(self):
        astar = mock.MagicMock(spec=AStar)
        after = 0x10000 - 1
        astar.read_encoders.side_effect = [(1, 1), (after, after)]
        e = Encoders(astar)
        e.read_encoders()
        self.assertEqual((-2, -2), e.read_encoders())

