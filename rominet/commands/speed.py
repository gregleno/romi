from rominet.commands.command import Command


class Speed(Command):

    def __init__(self, speed_left, speed_right):
        super(Speed, self).__init__()
        self.speed_left = speed_left
        self.speed_right = speed_right

    def set_target_speed(self, speed_left, speed_right):
        self.speed_left = speed_left
        self.speed_right = speed_right

    def get_motor_speeds(self, situation):
        return self.speed_left, self.speed_right
