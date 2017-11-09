from rominet.motors import Motors


def test_cap_acceleration():
    """Test that no cp happens if we accelerate by half the max acceleration."""

    last_speed_cmd = Motors.max_speed / 10
    speed_cmd = last_speed_cmd + Motors.max_acceleration / 2
    assert Motors.cap_acceleration(speed_cmd, last_speed_cmd) == speed_cmd

    # Same with negative speed values
    assert Motors.cap_acceleration(-speed_cmd, -last_speed_cmd) == -speed_cmd


def test_cap_acceleration_accelerate_too_fast():
    """Test that no cp happens if we accelerate by half the max acceleration."""

    last_speed_cmd = Motors.max_speed / 10
    speed_cmd = last_speed_cmd + Motors.max_acceleration * 2
    assert Motors.cap_acceleration(speed_cmd,
                                   last_speed_cmd) == (last_speed_cmd + Motors.max_acceleration)

    # Same with negative speed values
    assert Motors.cap_acceleration(-speed_cmd,
                                   -last_speed_cmd) == (-last_speed_cmd - Motors.max_acceleration)


def test_cap_acceleration_decelerate_too_fast():
    """Test that no cp happens if we accelerate by half the max acceleration."""

    last_speed_cmd = Motors.max_speed / 10
    speed_cmd = last_speed_cmd - Motors.max_acceleration * 2
    assert Motors.cap_acceleration(speed_cmd,
                                   last_speed_cmd) == (last_speed_cmd - Motors.max_acceleration)

    # Same with negative speed values
    assert Motors.cap_acceleration(-speed_cmd,
                                   -last_speed_cmd) == (-last_speed_cmd + Motors.max_acceleration)


def test_convert_command_to_speed():
    assert Motors.convert_command_to_speed(0.5) == Motors.max_speed / 2
    assert Motors.convert_command_to_speed(-0.5) == -Motors.max_speed / 2
    assert Motors.convert_command_to_speed(2) == Motors.max_speed
    assert Motors.convert_command_to_speed(-2) == -Motors.max_speed
