# -*- coding: utf-8 -*-
"""
Created on 26.04.2019

@author: beckmann
"""
import math

from math import atan

import numpy
from solid import rotate, translate, cube, cylinder, mirror, hole, scad_render_to_file

from Holmos import strut_with_holes
import base
from file_tools import safe_mkdir
from helpers import rounded_plate


def rpi_mount(assemble=False, hole_diam=3):
    """Mount for Raspberry Pi using four screws.
    Clipped to side of cage.
    Requires four cylindrical spacers.
    RPi is in (optical) XZ-plane.
    Plate is printed in (printer) XY plane
    https://www.raspberrypi.org/documentation/hardware/raspberrypi/mechanical/rpi_MECH_3bplus.pdf"""
    hole_sep_z = 58
    hole_sep_x = 49

    strut_width = 10
    strut_thick = 3

    hole_diagonal = (hole_sep_x**2 + hole_sep_z**2)**.5

    strut_angle_deg = numpy.rad2deg(numpy.arctan(hole_sep_x/hole_sep_z))  # angle < 45°

    diag_strut = strut_with_holes(hole_diagonal, strut_thick, strut_width, hole_diam=hole_diam)

    cross = rotate((0, 0, -strut_angle_deg))(diag_strut)
    cross += rotate((0, 0, strut_angle_deg))(diag_strut)
    cross = translate((0, 0, +strut_thick/2))(cross)  # to z=0...-thick,

    baseplate = base.base(rod_sep=base.rods30_diag_third_rod)  # works for threads20 as well: superfluous kwargs are ignored.
    mount_strut = rotate((-90, 0, 0))(translate((0, 20, 0))(baseplate))  # from optical-axis coords to our coords.
    cross += translate((0, hole_sep_z/2-strut_width, 0))(mount_strut)
    cross += translate((0, -hole_sep_z/2+strut_width, 0))(mount_strut)

    if assemble:
        cross = translate((20, -base.rods30_diag_third_rod / 2 - 25, 0))(rotate((90, 0, -90))(cross))
    else:
        spacer_height = 5
        spacer = cylinder(d=2*hole_diam, h=spacer_height, center=True)
        spacer -= cylinder(d=1.2*hole_diam, h=spacer_height+1, center=True)
        for x in [15, 15 + 2.5*hole_diam, -15, -15 - 2.5 * hole_diam]:
            cross += translate((x, 0, spacer_height/2))(spacer)

    return cross


def cage_stabilizer(assemble=False):
    """stabilizer with 3 clamps for HolMOS-cage"""

    cage_base = 30
    stabilizer_base = base.rods30_dist_third_rod
    stabilizer_height = 10

    angle = -atan(cage_base/2/stabilizer_base)/math.pi*180

    stabilizer = translate((0,stabilizer_base/2,0))(cube((cage_base+4,stabilizer_base-10,stabilizer_height), center=True))

    stabilizer -= translate((-cage_base,stabilizer_base/2,0))(rotate((0,0,angle))(cube((cage_base,stabilizer_base,2*stabilizer_height), center=True)))
    stabilizer -= translate((cage_base,stabilizer_base/2,0))(rotate((0,0,-angle))(cube((cage_base,stabilizer_base,2*stabilizer_height), center=True)))

    stabilizer = translate((0, -25, 0))(stabilizer)

    for (dd, y) in ((25, 0), (10, 21)):
        stabilizer -= translate((0, y, 0))(cylinder(d=dd, h=20, center=True))

    stabilizer += cage_3_clips()

    return stabilizer


def cage_3_clips(z_length=10, inside=False):
    """3 clips arranged in proper distances for cage, aligned to optical axis at 0,0."""
    third_rod_y = base.rods30_dist_third_rod-25  # main pair of rods is at y=-25

    clip_pair = base.base(z_length=z_length)
    single_clip = base.single_rod_clamp(z_length)

    if inside:
        clip_pair = translate((0, -50, 0))(mirror((0, 1, 0))(clip_pair))  # clip at 25, needs to be moved back.
        single_clip = mirror((0, 1, 0))(single_clip)

    single_clip = translate((0, third_rod_y, 0))(rotate((0, 0, 180))(single_clip))
    return clip_pair + single_clip


def cage_side_stabilizer():
    """stabilizer for both sides of new HolMOS-Cage"""

    sep_z = 100
    sep_x = base.rods30_diag_third_rod

    strut_width = 10
    strut_thick = 3

    diagonal = (sep_x**2 + sep_z**2)**.5

    strut_angle_deg = numpy.rad2deg(numpy.arctan(sep_x/sep_z))  # angle < 45°

    diag_strut = rounded_plate((strut_width, diagonal+strut_width, strut_thick), strut_width/2)

    cross = rotate((0, 0, -strut_angle_deg))(diag_strut)
    cross += rotate((0, 0, strut_angle_deg))(diag_strut)

    cross = translate((0, 0, -strut_thick/2))(cross)  # to z=0...-thick,

    mount_strut = cube((sep_x, strut_width, strut_thick), center=True)
    mount_strut = translate((0, 0, -strut_thick/2))(mount_strut)  # to z=0...-thick,
    mount_strut += rotate((-90,0,0))(translate((0,20,0))(base.base_rods30(rod_sep=sep_x)))  # from optical-axis coords to our coords.
    cross += translate((0, sep_z/2, 0))(mount_strut)
    cross += translate((0, -sep_z/2, 0))(mount_strut)

    return cross


def cage_base_plate(assemble=False):
    """base_plate with 3 clamps for new HolMOS-Cage"""

    cage_base = 30
    stabilizer_base = 60
    stabilizer_height = 10

    angle = -atan(cage_base/2/stabilizer_base)/math.pi*180

    plate = translate((0, stabilizer_base/2, 0))(cube((cage_base+4, stabilizer_base-10, stabilizer_height), center=True))

    plate -= translate((-cage_base, stabilizer_base/2, 0))(rotate((0, 0, angle))(cube((cage_base, stabilizer_base, 2*stabilizer_height), center=True)))
    plate -= translate((cage_base, stabilizer_base/2, 0))(rotate((0, 0, -angle))(cube((cage_base, stabilizer_base, 2*stabilizer_height), center=True)))

    for y in (15, 40):
        plate += hole()(translate([0, y, 5])(cylinder(d=12, center=True, h=10)))
        plate += hole()(translate([0, y, -5])(cylinder(d=7.5, center=True, h=2*10)))

    for y in (10, stabilizer_base-5):
        strut_thick = 3
        strut = strut_with_holes(hole_dist=40, strut_thick=strut_thick, strut_width=10)
        plate += translate((0, y, (strut_thick-10)/2))(rotate((0, 0, 90))(strut))

    plate = translate((0, -25, 0))(plate)

    plate += translate((0,0,10))(cage_3_clips(z_length=30))

    return plate


def board_hook(clip_z=30, hook_opening=18, assemble=False):
    """
    Hook for topmost end of cage - can be used to hang setup from a door, whiteboard, poster board, cabinet...
    2019-05-13 - printed, works well. But: real-life poster board is one inch thick.
    """
    assert base.__rods30, "this only makes sense for rod-mount"

    rod_clips = base.base_rods30(z_length=clip_z)
    rod_clips = translate((0, 0, clip_z / 2))(rod_clips)  # start at z=0

    hook_thick = 4
    hook_width = 30
    hook_z = 35

    strut_height = 10

    hook = translate((0, hook_opening - 20 + hook_thick / 2))(cube((hook_width, hook_thick, hook_z), True))
    hook = translate((0, 0, hook_z/2))(hook)

    strut = cube((hook_thick, hook_opening+.1, strut_height), True)
    strut = translate((hook_width/2-hook_thick, (hook_opening-40)/2, strut_height/2))(strut)
    strut += mirror((1, 0, 0))(strut)

    assembly = rod_clips + hook + strut

    if assemble:
        return translate((0, -50, 0))(rotate((0, 180, 180))(assembly))
    else:
        return assembly


def cage_circumference(d_outer=80.5, wall_thick=2, h=10,assemble=None):
    """Circle to fit cage ends, e.g. to transport cage inside a cylindrical tube"""
    d_inner = base.rods30_dist_third_rod+7  # absolute diameter: contact to clips.

    clamp = translate((0, 0, 5))(cage_3_clips(inside=True))  # bottom at z=0
    circ_x_at_clamp = ((d_outer/2)**2 - 30**2)**.5
    back_face = cube((2*circ_x_at_clamp, wall_thick, h), center=True)
    back_face = translate((0, -30+wall_thick/2, h/2))(back_face)

    circle = cylinder(d=d_outer, h=h)
    circle -= translate((0, 0, wall_thick))(cylinder(d=d_outer-2*wall_thick, h=2*h))  # relative diameter: wall thickness
    circle -= translate((0, 0, -2))(cylinder(d=d_inner, h=2*h))

    # clear space past -y of clamps, so that cage can rest against wall when used with hook.
    helper_block_y = 30
    circle -= translate((0, -20-10-helper_block_y/2, 0))(cube((100, helper_block_y, 100), center=True))

    # add some holes to screw cage onto something
    for angle_deg in (-30, 30, 150, 210):
        hole_position = lambda obj: rotate(angle_deg)(translate((d_inner/2, 0, 0))(obj))
        circle += hole_position(cylinder(d=8, h=wall_thick))
        circle -= hole_position(cylinder(d=3.2, h=2*h, center=True))

    return clamp + circle + back_face


if __name__ == "__main__":
    import os

    _fine = True
    render_STL = False

    if _fine:
        header = "$fa = 5;"  # minimum face angle
        header += "$fs = 0.1;"  # minimum face size
    else:
        header = ""

    safe_mkdir("scad/misc")

    scad_render_to_file(cage_stabilizer(), "scad/misc/Cage_Stabilizer.scad", file_header=header)

    scad_render_to_file(cage_side_stabilizer(), "scad/misc/Cage_Side_Stabilizer.scad", file_header=header)

    scad_render_to_file(cage_base_plate(), "scad/misc/Cage_Base_Plate.scad", file_header=header)

    scad_render_to_file(rpi_mount(), "scad/misc/rpi_mount.scad", file_header=header)

    scad_render_to_file(board_hook(), "scad/misc/wall_hook.scad", file_header=header)

    scad_render_to_file(cage_circumference(), "scad/misc/cage_circumference.scad", file_header=header)
