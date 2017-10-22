class PID(object):
    def __init__(self, Kp=1, Ki=0, Kd=0, max_abs_value=1, print_i=False):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.max_abs_value = max_abs_value
        self.error = 0
        self.error_integration = 0
        self.error_derivative = 0
        self.previous_error = 0
        self.previous_time = 0
        self.print_i = print_i

    def get_output(self, set_point, read_value, current_time):
        if self.previous_time != 0:
            step = float(current_time - self.previous_time)
        else:
            step = 0

        self.previous_error = self.error
        self.error = set_point - read_value
        self.error_integration += self.error * step
        if step != 0:
            self.error_derivative = (self.error - self.previous_error) / step

        self.previous_time = current_time

        value = (self.Kp * self.error +
                 self.Ki * self.error_integration +
                 self.Kd * self.error_derivative)

        if self.print_i and set_point != 0:
            print("setpoint: {}".format(int(set_point)))
            print("P: {} Kp*E: {}".format(int(self.error), int(self.Kp * self.error)))
            print("I: {} Ki*I: {}".format(int(self.error_integration), int(self.Ki * self.error_integration)))
            print("D: {} Kd*D: {}\n".format(int(self.error_derivative), int(self.Kd * self.error_derivative)))
        if value > self.max_abs_value:
            value = self.max_abs_value
        if value < -self.max_abs_value:
            value = -self.max_abs_value
        return value

    def reset(self):
        self.error = 0
        self.error_integration = 0
        self.error_derivative = 0
        self.previous_error = 0
        self.previous_time = 0
