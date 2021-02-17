#!/usr/bin/env python3

import enum

class ElementType(enum.Enum):
    ARC     = 1
    FILL    = 2
    PAD     = 3
    STRING  = 4
    TRACK   = 5
    VIA     = 6
    COMP    = 7

class Rotation(enum.Enum):
    R0      = 0
    R90     = 1
    R180    = 2
    R270    = 3

# 0: no quadrants
# 1: third quadrant (ur)
# 2: second quadrant (ul)
# 4: first quadrant (dl)
# 8: fourth quadrant (dr)
class Quadrants():
    ur  = None
    ul  = None
    dl  = None
    dr  = None

    def __init__(self, value):
        self.ur = (value & 1) != 0
        self.ul = (value & 2) != 0
        self.dl = (value & 4) != 0
        self.dr = (value & 8) != 0

class Layer(enum.Enum):
    TOP             = 1
    MID_1           = 2
    MID_2           = 3
    MID_3           = 4
    MID_4           = 5
    BOTTOM          = 6
    TOP_OVERLAY     = 7
    BOTTOM_OVERLAY  = 8
    GROUND_PLANE    = 9
    POWER_PLANE     = 10
    BOARD           = 11
    KEEP_OUT        = 12
    MULTI           = 13

class Shape(enum.Enum):
    CIRCULAR        = 1
    RECTANGULAR     = 2
    OCTAGONAL       = 3
    ROUNDRECT       = 4
    CROSSHAIR       = 5
    MOIRE           = 6

class Plane(enum.Enum):
    NONE            = 1
    RELIEF_GROUND   = 2
    DIRECT_GROUND   = 3
    RELIEF_POWER    = 4
    DIRECT_POWER    = 5
