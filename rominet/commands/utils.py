from math import pi


def get_yaw_delta(set_point_yaw, yaw, pid, current_time):
    if set_point_yaw - yaw > pi:
        yaw = yaw + 2 * pi
    elif set_point_yaw - yaw < -pi:
        yaw = yaw - 2 * pi
    return pid.get_output(set_point_yaw, yaw, current_time)
