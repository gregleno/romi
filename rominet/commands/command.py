class Command(object):

    def __init__(self):
        self.achieved = False

    def get_motor_speeds(self, situation):
        raise NotImplemented()

    def is_achieved(self):
        return self.achieved
