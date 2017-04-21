class Encoders:

    def __init__(self, a_star):
        self.a_star = a_star
        self.count_left = 0
        self.count_right = 0
        self.last_count_left = 0
        self.last_count_right = 0
        self.count_sign_left = 1
        self.count_sign_right = -1

    def read_encoders(self):
        count_left, count_right = self.a_star.read_encoders()

        diff_left = (count_left - self.last_count_left) % 0x10000
        if diff_left >= 0x8000:
            diff_left -= 0x10000

        diff_right = (count_right - self.last_count_right) % 0x10000
        if diff_right >= 0x8000:
            diff_right -= 0x10000

        self.count_left += self.count_sign_left * diff_left
        self.count_right += self.count_sign_right * diff_right

        self.last_count_left = count_left
        self.last_count_right = count_right

        return self.count_left, self.count_right
