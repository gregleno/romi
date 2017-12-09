from math import radians
from rominet.commands import MoveStraight


def test_move_simple():
    command = MoveStraight(1, 1, 0, 0)
    left, right = command.get_motor_speeds(0, 0, 0, 0, 0, 0, 0, 0)
    assert left == right
    assert left > 0


def test_move_reverse_simple():
    command = MoveStraight(-1, 1, 0, 0)
    left, right = command.get_motor_speeds(0, 0, 0, 0, 0, 0, 0, 0)
    assert left == right
    assert left < 0


def test_move_rotate_right():
    """ Check that if the robot deviate we correct the rotation"""
    command = MoveStraight(1, 1, 0, 0)
    left, right = command.get_motor_speeds(0, 0, 0, 0, radians(5), 0, 0, 0)
    assert left < right


def test_move_rotate_left():
    """ Check that if the robot deviate we correct the rotation"""
    command = MoveStraight(1, 1, 0, 0)
    left, right = command.get_motor_speeds(0, 0, 0, 0, radians(-5), 0, 0, 0)
    assert left > right


def test_destination_reached():
    """ Check that we stop the robot when we arrive at destination """

    command = MoveStraight(1, 1, 0, 0)
    left, right = command.get_motor_speeds(0, 0, 0, 0, 0, 0, 1, 0)
    assert command.is_achieved()
    assert left == right == 0


def test_destination_exceeded():
    """ Check that we stop the robot if we overshoot """
    command = MoveStraight(1, 1, 0, 0)
    left, right = command.get_motor_speeds(0, 0, 0, 0, 0, 0, 1.1, 0)
    assert command.is_achieved()
    assert left == right == 0


def test_destination_not_reached():
    command = MoveStraight(1, 1, 0, 0)
    command.get_motor_speeds(0, 0, 0, 0, 0, 0, 0.9, 0)
    assert not command.is_achieved()
