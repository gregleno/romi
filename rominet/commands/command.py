class Command(object):

    def __init__(self):
        self.achieved = False

    def get_motor_speeds(self, speed_left, speed_right, x, y, yaw, omega, distance, current_time):
        return 0, 0

    def is_achieved(self):
        return self.achieved
