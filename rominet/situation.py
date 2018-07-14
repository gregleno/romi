from collections import namedtuple


Situation = namedtuple("Situation",
                       ("current_time", "x", "y", "yaw", "omega", "dist", "speed_l", "speed_r",
                        "velocity"))
