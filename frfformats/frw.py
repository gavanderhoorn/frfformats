# Software License Agreement (Apache License)
#
# Copyright 2015 TU Delft Robotics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: G.A. vd. Hoorn - TU Delft Robotics Institute
#


# actually enum34
from enum import Enum


class FrwShapeKind(Enum):
    # this is a kludge, perhaps extend class hierarchy for this
    CAD = -2
    UNKNOWN = -1
    BOX = 0
    SPHERE = 2
    CYLINDER = 3


class FrwObjectScale(object):
    """
    Scale in RG is in millimeters, file stores this as float divided by 1000,
    which makes it look like meters.
    """
    def __init__(self):
        self.x = 1.
        self.y = 1.
        self.z = 1.

    def __str__(self):
        return "(%.3f; %.3f; %.3f)" % (self.x, self.y, self.z)


class FrwTriad(object):
    """
    A 'frame' or 'coordinate frame' in a 6D Cartesian space.

    Keeps Fanuc (XYZ, WPR) conventions.

    Positional part is in millimeters.
    Orientation part is in degrees.
    """
    def __init__(self):
        self.x = 0.
        self.y = 0.
        self.z = 0.
        self.w = 0.
        self.p = 0.
        self.r = 0.

    def __str__(self):
        return "(%.3f; %.3f; %.3f; %.3f; %.3f; %.3f)" % (
            self.x, self.y, self.z, self.w, self.p, self.r)

    def pos(self):
        """
        :returns: Tuple of just the position part of this Triad
        """
        return (self.x, self.y, self.z)

    def orient(self):
        """
        :returns: Tuple of just the orientation part of this Triad
        """
        return (self.w, self.p, self.r)

    def as_tuple(self):
        return (self.x, self.y, self.z, self.w, self.p, self.r)

    def as_rpy(self):
        """
        :returns: Tuple (3 floats) of Triad orientation in (roll, pitch, yaw) order
        """
        return (self.r, self.p, self.w)

    def all_zeros(self):
        """
        :returns: ``True`` iff all elements of this Triad are equal to zero, ``bool``
        """
        return all([c == 0. for c in self.as_tuple()])


class FrwColour(object):
    """
    TODO: https://pypi.python.org/pypi/colour/
    """
    def __init__(self):
        self.r = 0.
        self.g = 0.
        self.b = 0.
        self.a = 1.

    def __str__(self):
        return "(%.3f; %.3f; %.3f; %.3f)" % (self.r, self.g, self.b, self.a)

    def set_from_hex_str(self, vb_str):
        # interpret str as hex
        clr = int(vb_str[2:], 16)
        # bgr triplet
        self.b = float((clr >> (2 * 8)) & 0xFF) / 255.0
        self.g = float((clr >> (1 * 8)) & 0xFF) / 255.0
        self.r = float((clr >> (0 * 8)) & 0xFF) / 255.0
        # we assume alpha always 1
        self.a = 1.

    def as_rgba_tuple(self):
        return (self.r, self.g, self.b, self.a)

    def as_rgba_tuple_int(self):
        return (
            int(round(self.r * 255.0)),
            int(round(self.g * 255.0)),
            int(round(self.b * 255.0)),
            int(round(self.a * 255.0)))


class FrwObject(object):
    """
    Anything in the FRW file (that can be considered an object)
    """
    def __init__(self, id):
        if type(id) is not int:
            raise ValueError("'id' must be an integer")
        self.id = id

    def __str__(self):
        return "(id: %d)" % (self.id)


class FrwChuiObject(FrwObject):
    """
    Anything that can be placed in the 3D world (or CHUI)
    """
    def __init__(self, id):
        super(FrwChuiObject, self).__init__(id)
        # for some objects, the rotation part will be ignored
        self.location = FrwTriad()


class FrwCellObject(FrwChuiObject):
    """
    """
    def __init__(self, id):
        super(FrwCellObject, self).__init__(id)
        self.scale = FrwObjectScale()
        self.colour = FrwColour()
        self.kind = FrwShapeKind.UNKNOWN
        self.name = 'Obstacle'

        # TODO: perhaps store this in a class
        self.cad_imglib_loc_rel = ''
        self.cad_imglib_loc_abs = ''
        self.cad_file_cached = ''


class FrwUserFrame(FrwChuiObject):
    def __init__(self, id):
        super(FrwUserFrame, self).__init__(id)
        self.name = 'UFrame'
        self.num = -1

    def __str__(self):
        return "FrwUFrame('%s' (%d))" % (self.name, self.num)


class FrwEoat(FrwChuiObject):
    def __init__(self, id):
        super(FrwEoat, self).__init__(id)
        self.name = 'Eoat'
        self.num = -1
        self.mass = 0.0

    def __str__(self):
        return "FrwEoat('%s' (%d))" % (self.name, self.num)


class FrwRobotController(FrwObject):
    def __init__(self, id):
        super(FrwRobotController, self).__init__(id)
        self.robot_groups = []

        self.name = ''
        self.vcr_version = ''
        self.vcr_build_id = ''
        self.orderfil_dat = ''
        self.app_tool_order_number = ''
        self.app_tool_title = ''


class FrwRobotGroup(FrwObject):
    def __init__(self, id):
        super(FrwRobotGroup, self).__init__(id)
        self.eoats = []
        self.user_frames = []

        self.name = ''
        self.model_name = ''
        self.active_uframe_num = 0
        self.location = FrwTriad()


class FrwWorkcell(object):
    def __init__(self):
        self.obstacles = []
        self.fixtures = []
        self.robot_controllers = []
        self.machines = []

        self.name = ''
        self.description = ''
        self.version = ''
        # not populated/used right now
        self.build_ids = {}

    def __str__(self):
        return ("FrmWorkCell '%s' (%d obstacle(s), %d fixture(s), %d controller(s), "
            "%d machine(s))" % (self.name, len(self.obstacles),
            len(self.fixtures), len(self.robot_controllers), len(self.machines)))
