#!/usr/bin/env python

from flask import Flask, jsonify, make_response, request, abort
from robot import Robot

app = Flask("rominet")
robot = None

# TODO: switch to flask restful
# see https://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/rominet/api/leds', methods=['PUT'])
def set_leds():
    if not request.json:
        abort(400)
    if 'leds' not in request.json or type(request.json['leds']) is not int:
        abort(400)
    leds = request.json['leds']
    try:
        robot.set_leds(leds)
        return jsonify({'leds': leds})
    except IOError:
        return jsonify({'connected': False})


@app.route('/rominet/api/reboot', methods=['GET'])
def reboot():
    robot.stop()
    os.system("sudo reboot")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/rominet/api/status', methods=['GET'])
def get_status():
    try:
        return jsonify({'battery': robot.get_battery(),
                        'connected': True,
                        'position': robot.get_position_XY(),
                        'speed': robot.get_speed(),
                        'buttons': robot.read_buttons()})
    except IOError:
        return jsonify({'connected': False})


def run_web_server(rob):
    global robot
    robot = rob
    app.run(debug=True, host="0.0.0.0")


class RobotTest(Robot):
    def move(self, left, right):
        pass

    def stop(self):
        pass

    def read_buttons(self):
        return 3

    def get_position_XY(self):
        return (1, 2)

    def get_distance(self):
        return 7

    def get_speed(self):
        return 0

    def get_battery(self):
        return 7200

    def set_leds(self, leds):
        pass

    def is_romi_board_connected(self):
        return True

if __name__ == '__main__':
    run_web_server(RobotTest())
