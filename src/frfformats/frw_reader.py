#!/usr/bin/python

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

try:
    import xml.etree.cElementTree as et
except:
    import xml.etree.ElementTree as et

from frfformats.frw import FrwWorkcell, FrwObstacle, FrwFixture, FrwUserFrame, FrwEoat, FrwRobotController, FrwRobotGroup, FrwShapeKind


def _parse_obj(elem, obj):
    obj.name = elem.get('Name')
    # if an obstacle doesn't have a 'Kind' attribute, it is always (?) a CAD object
    # TODO: should we perform some kind of validation here?
    obj.kind = FrwShapeKind(int(elem.get('Kind', FrwShapeKind.CAD.value)))

    # pose, scaling
    obj.location.x = float(elem.get('LocationX', 0.))
    obj.location.y = float(elem.get('LocationY', 0.))
    obj.location.z = float(elem.get('LocationZ', 0.))
    obj.location.w = float(elem.get('LocationW', 0.))
    obj.location.p = float(elem.get('LocationP', 0.))
    obj.location.r = float(elem.get('LocationR', 0.))

    obj.scale.x = float(elem.get('ScaleX', 1.))
    obj.scale.y = float(elem.get('ScaleY', 1.))
    obj.scale.z = float(elem.get('ScaleZ', 1.))

    # object colour (default to black)
    obj.colour.set_from_vb_str(elem.get('Color', '&H0'))

    if 'CADFileName' in elem.attrib:
        # this should be a CAD obstacle
        if not obj.kind == FrwShapeKind.CAD:
            raise ValueError("Obstacle '%s' has 'CADFileName' attribute,"
                " but is not a CAD obj kind ('%s')" % (obj.name, obj.kind))

        # TODO: not so nice
        obj.cad_imglib_loc_abs = elem.get('CADFileName')
        cad_file_e = elem.find('CADFile')
        obj.cad_imglib_loc_rel = cad_file_e.get('CADFile')
        obj.cad_file_cached = cad_file_e.get('CachedCADFile')


def load_stream(istr):
    wcell = FrwWorkcell()
    root = et.fromstring(istr.read())

    # metadata
    wcell.name = root.get('Name')
    wcell.description = root.get('Description')
    wcell.version = root.get('Version')

    # TODO: do this in a more dynamic way (register parsers in dict, then
    # call appropriate function according to Frw Object Type or something)


    # obstacles
    # we use findall() here in case there is more than one 'Obstacles' tag
    for obs_es in root.findall('Obstacles'):
        for obs_e in obs_es.findall('Obstacle'):
            obs = FrwObstacle(int(obs_e.get('ID')))
            _parse_obj(obs_e, obs)
            wcell.obstacles.append(obs)


    # fixtures
    # we use findall() here in case there is more than one 'Fixtures' tag
    for fixts_es in root.findall('Fixtures'):
        for fixt_e in fixts_es.findall('Fixture'):
            fixt = FrwFixture(int(fixt_e.get('ID')))
            _parse_obj(fixt_e, fixt)
            wcell.fixtures.append(fixt)


    # controllers
    # we use findall() here in case there is more than one 'RobotControllers' tag
    for rctrlrs_es in root.findall('RobotControllers'):
        for rctrlr_e in rctrlrs_es.findall('RobotController'):
            rctrlr = FrwRobotController(int(rctrlr_e.get('ID')))
            rctrlr.name = rctrlr_e.get('Name')

            # controller groups
            for rgrps_es in rctrlr_e.findall('RobotGroups'):
                for rgrp_e in rgrps_es.findall('RobotGroup'):
                    rgrp = FrwRobotGroup(int(rgrp_e.get('ID')))

                    rgrp.name = rgrp_e.get('Name')
                    rgrp.model_name = rgrp_e.get('ModelName')

                    # TODO: this will only read the active uframe num for the first occurence of 'UserFrames'
                    rgrp.active_uframe_num = int(rgrp_e.find('UserFrames').get('ActiveUFrameNum'))

                    for uframes_es in rgrp_e.findall('UserFrames'):
                        for uframe_e in uframes_es.findall('UserFrame'):
                            uframe = FrwUserFrame(int(uframe_e.get('ID')))

                            uframe.name = uframe_e.get('Name')
                            uframe.num = int(uframe_e.get('UFrameNum'))

                            uframe.location.x = float(uframe_e.get('FrameX', 0))
                            uframe.location.y = float(uframe_e.get('FrameY', 0))
                            uframe.location.z = float(uframe_e.get('FrameZ', 0))
                            uframe.location.w = float(uframe_e.get('FrameW', 0))
                            uframe.location.p = float(uframe_e.get('FrameP', 0))
                            uframe.location.r = float(uframe_e.get('FrameR', 0))

                            rgrp.user_frames.append(uframe)

                    for eoats_es in rgrp_e.findall('EOATs'):
                        for eoat_e in eoats_es.findall('EOAT'):
                            eoat = FrwEoat(int(eoat_e.get('ID')))

                            eoat.name = eoat_e.get('Name')
                            eoat.num = int(eoat_e.get('UToolNum'))
                            eoat.mass = float(eoat_e.get('MassKG', '0'))

                            eoat.location.x = float(eoat_e.get('LocationTCPX', 0))
                            eoat.location.y = float(eoat_e.get('LocationTCPY', 0))
                            eoat.location.z = float(eoat_e.get('LocationTCPZ', 0))
                            eoat.location.w = float(eoat_e.get('LocationTCPW', 0))
                            eoat.location.p = float(eoat_e.get('LocationTCPP', 0))
                            eoat.location.r = float(eoat_e.get('LocationTCPR', 0))

                            rgrp.eoats.append(eoat)

                    rctrlr.robot_groups.append(rgrp)

            wcell.robot_controllers.append(rctrlr)


    # TODO: Parts, PartRacks, ViewPoints, WorkcellFrames, Machines, etc


    return wcell


def load_file(filename):
    with open(filename, 'r') as f:
        return load_stream(f)


if __name__ == '__main__':
    import argparse

    # parse command line opts
    parser = argparse.ArgumentParser()
    parser.add_argument('file_input', type=str, metavar='INPUT',
            help="Roboguide Work Cell file (*.frw)")

    # handle all arguments
    args = parser.parse_args()

    cell = load_file(args.file_input)

    print cell
