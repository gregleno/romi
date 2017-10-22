#!/usr/bin/env python

import os
import logging
from math import pi

from flask import Flask, jsonify, make_response, request, abort, render_template, redirect
# from rominet.robot import Robot


app = Flask("rominet")
robot = None


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/rominet/api/leds', methods=['PUT'])
def set_leds():
    if not request.json:
        abort(400)
    if 'red' not in request.json or type(request.json['red']) is not int:
        abort(400)
    if 'yellow' not in request.json or type(request.json['yellow']) is not int:
        abort(400)
    if 'green' not in request.json or type(request.json['green']) is not int:
        abort(400)
    red = request.json['red']
    yellow = request.json['yellow']
    green = request.json['green']
    try:
        robot.set_leds(red, yellow, green)
        return jsonify({})
    except IOError:
        return jsonify({'connected': False})


@app.route("/rominet/api/notes", methods=['PUT'])
def play_notes():
    if not request.json:
        abort(400)
    if 'notes' not in request.json or type(request.json['notes']) is not unicode:
        abort(400)
    try:
        robot.play_notes(request.json['notes'])
        return jsonify({})
    except IOError:
        return jsonify({'connected': False})


@app.route('/rominet/api/camera')
def camera():
    return robot.get_camera_frame()


@app.route('/rominet/api/shutdown', methods=['GET'])
def reboot():
    try:
        robot.stop()
    except IOError:
        pass
    os.system("sudo halt")
    return redirect("/shutdown")


@app.route('/rominet/api/reset_odometry', methods=['GET'])
def reset_odometry():
    robot.reset_odometry()
    return jsonify({})


# TODO only return this for api calls
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/rominet/api/motors", methods=['PUT'])
def motors():
    if 'left' not in request.json or type(request.json['left']) is not int:
        abort(400)
    if 'right' not in request.json or type(request.json['right']) is not int:
        abort(400)
    left = request.json['left']
    right = request.json['right']
    try:
        robot.set_speed_target(left/100., right/100.)
        return jsonify({})
    except IOError:
        return jsonify({'connected': False})


@app.route("/rominet/api/rotate", methods=['PUT'])
def rotate():
    if 'angle' not in request.json or type(request.json['angle']) is not int:
        abort(400)
    if 'speed' not in request.json or type(request.json['speed']) is not int:
        abort(400)
    angle = request.json['angle'] * pi / 180.
    speed = request.json['speed'] * pi / 180.
    try:
        robot.rotate(angle, speed)
        return jsonify({})
    except IOError:
        return jsonify({'connected': False})


@app.route("/rominet/api/move_forward", methods=['PUT'])
def move_forward():
    if ('distance' not in request.json or type(request.json['distance']) is not float or
       'speed' not in request.json or type(request.json['speed']) is not int):
        abort(400)
    try:
        robot.move_forward(request.json['distance'], request.json['speed']/100.)
        return jsonify({})
    except IOError:
        return jsonify({'connected': False})


@app.route('/rominet/api/status')
def get_status():
    try:
        data = {'battery': robot.get_battery(),
                'connected': True,
                'position': robot.get_position_xy(),
                'encoders': robot.get_encoders(),
                'speed': robot.get_speed(),
                'distance': robot.get_distance(),
                'yaw': robot.get_yaw(),
                'buttons': robot.read_buttons()}
        return jsonify(data)
    except IOError:
        return jsonify({'connected': False})


def run_web_server(rob, debug=False):
    global robot
    robot = rob
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(debug=debug, host="0.0.0.0", threaded=True)
