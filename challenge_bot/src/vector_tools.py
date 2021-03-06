#!/usr/bin/env python

# Emily Wang, Eric Schneider
# Computational Robotics, Fall 2014, Olin College, taught by Paul Ruvolo
# This code has basic tools for working with Vector3 vectors

from math import atan2, cos, sin, copysign, pi
from geometry_msgs.msg import Vector3

def vector_add(v1, v2):
    v = Vector3()
    v.x = (v1.x + v2.x)
    v.y = (v1.y + v2.y)
    v.z = (v1.z + v2.z)
    return v

def vector_multiply(v1, scalar):
    v = Vector3()
    v.x = v1.x * scalar
    v.y = v1.y * scalar
    v.z = v1.z * scalar
    return v

def vector_mag(v):
    mag = pow(pow(v.x, 2) + pow(v.y, 2), 0.5)
    return mag

# Angle assumes 2D vector, returns in radians
# Horizontal (1, 0) is an angle of 0, sweeps (+/-) going (CCW/CW)
def vector_ang(v):
    ang = -atan2(-v.y, v.x)
    return ang

def create_angled_vector(angle=0.0, magnitude=1.0):
    """
    Creates a vector at the desired angle, with the desired strength
    """
    x = cos(angle)
    y = sin(angle)
    v = Vector3(x, y, 0)
    return vector_multiply(v, magnitude)

def create_unit_vector(v1):
    v = Vector3()
    if vector_mag(v1) == 0:
        v.x = 1.0
    else:
        v.x = v1.x / vector_mag(v1)
        v.y = v1.y / vector_mag(v1)
    return v

def add_angles(angle, addition):
    """
    Add angles (rad) and output an angle that is bounded from -/+ pi
    """
    added = angle + addition
    while abs(added) > pi:
        added -= 2 * pi * copysign(1, added)
    return added

def angle_difference(angle1, angle2):
    """
    Returns the angle FROM angle1 TO angle2, in radians
    """
    a = angle2 - angle1
    a = ((a + pi) % (2 * pi)) - pi
    return a