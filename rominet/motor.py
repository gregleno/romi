from pid import PID


class Motor(object):
    # 1440 ticks per rev, 150 rev per min 60 sec per minute
    MAX_SPEED = float(1440 * 150 / 60.)
    MAX_ACCELERATION = MAX_SPEED / 10  # Max speed achieved in 10 iterations
    MAX_CMD = 400.

    def __init__(self):
        self.pid_speed = PID(0.01, 0.9, 0, Motor.MAX_CMD)
        self.target_speed = 0

    @staticmethod
    def convert_command_to_speed(x):
        if x > 1:
            x = 1
        if x < -1:
            x = -1
        return x * Motor.MAX_SPEED

    def set_speed(self, target_speed):
        if abs(target_speed) > 1:
            print(target_speed)
            raise ValueError("The absolute value of target_speed "
                             "cannot be greater than 1, was: {}".format(target_speed))

        self.target_speed = self.convert_command_to_speed(target_speed)

    def get_speed_command(self, speed_measurement, time_of_measurement):
        speed_cmd = self.pid_speed.get_output(self.target_speed, speed_measurement,
                                              time_of_measurement)

        if self.target_speed == 0 and abs(speed_cmd) < 30:
            self.reset_pids()
            speed_cmd = 0

        return speed_cmd

    def reset_pids(self):
        self.pid_speed.reset()
