#!/usr/bin/env python
ser
# Emily Wang, Eric Schneider
# Computational Robotics, Fall 2014, Olin College, taught by Paul Ruvolo
# This code is the main class code for a robot that is prototyping the NASA
# sample challenge on a Neato robotics platform

import rospy
from geometry_msgs.msg import Twist, Vector3
from copy import deepcopy
from math import copysign

from vector_tools import *


class ChallengeBot():
    def __init__(self):
        rospy.init_node('ChallengeBot')

        # Sets the max/min velocity (m/s) and linear velocity (rad/s)
        self.MAX_LINEAR = 0.1
        self.MIN_LINEAR = 0.0
        self.MAX_ANGULAR = 0.3
        self.MIN_ANGULAR = 0.0
        self.DRIVE_CMDS = {"Right": Vector3(1, -1, 0),
                           "Left": Vector3(1, 1, 0),
                           "Forward": Vector3(1, 0, 0),
                           "Back": Vector3(-1, 0, 0)}

        # Cutoff magnitudes below which no drive command will be published
        self.CMD_CUTOFF = 0.01
        self.AVOID_CMD_CUTOFF = 0.1

        # Stores the start time as a float, not as a Time datatype
        self.start_time = rospy.get_time()
        # Time limit in seconds
        self.TIME_LIMIT = 10 * 60.0

        self.vector_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

        # TODO: Replace this with a subscription to /obstacle_avoid topic
        self.obs_avoid_vector = Vector3(0, 0, 0)

        self.unclaimed_samples = []
        self.claimed_samples = []

    def stop(self):
        """
        Publishes empty vector to stop robot
        """
        cmd = Twist()
        self.vector_pub.publish(cmd)

    def drive_distance(self, distance):
        """
        Drives a given distance straight forward or back, in meters
        """
        distance_cmd = Twist(linear=Vector3(copysign(0.25, distance), 0, 0))
        self.vector_pub.publish(distance_cmd)
        rospy.sleep(4 * abs(distance))
        self.stop()

    def time_left(self):
        """
        Returns the time left, in float seconds, until time is out
        """
        return (self.start_time + self.TIME_LIMIT) - rospy.get_time()

    def drive_angle(self, angle):
        """
        Drives a given angle, (CCW, CW) is (+/-). In radians
        """
        angle_cmd = Twist(angular=Vector3(0, 0, copysign(1, angle)))
        self.vector_pub.publish(angle_cmd)
        rospy.sleep(abs(angle))
        self.stop()

    def drive_robot(self, cmd_vector, avoid_obs=True):
        """
        Takes in a Vector3 direction in which to drive the robot, then layers
        the obstacle avoid vector on top of that, if asked to
        """
        if vector_mag(self.obs_avoid_vector) < self.AVOID_CMD_CUTOFF\
           or not avoid_obs:
            if vector_mag(cmd_vector) > self.AVOID_CMD_CUTOFF:
                self.drive(cmd_vector)
            else:
                self.stop()
        else:
            if vector_mag(cmd_vector) < self.AVOID_CMD_CUTOFF:
                self.drive(self.obs_avoid_vector)
            else:
                self.drive(vector_add(cmd_vector, self.obs_avoid_vector))

    def drive(self, vector):
        """
        Interprets a vector direction into a Twist command for the Neato
        """
        cmd = Twist()
        ang = vector_ang(vector)

        # Above this angle, turn towards the point (rad)
        forced_turn_angle = 1.5707963
        # Above this angle decrease speed, make a tighter turn (rad)
        max_speed_angle = 0.7853982

        if abs(ang) > forced_turn_angle:
            cmd.linear.x = self.MIN_LINEAR
        else:
            # Linear fit, 2.0x at 0, 1.0x at 45 and 0.0x at 90 degrees
            cmd.linear.x = (1 - ((abs(ang) - max_speed_angle)
                            / max_speed_angle)) * self.MAX_LINEAR
            cmd.linear.x = min(cmd.linear.x, self.MAX_LINEAR)

        if abs(ang) > forced_turn_angle:
            cmd.angular.z = copysign(1, ang) * self.MAX_ANGULAR
        else:
            cmd.angular.z = ang / forced_turn_angle * self.MAX_ANGULAR

        self.vector_pub.publish(cmd)
