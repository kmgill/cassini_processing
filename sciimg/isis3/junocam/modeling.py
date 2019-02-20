#!/usr/bin/env python2

import sys
import os
import spiceypy as spice
import math
import numpy as np
import argparse
import glob
from sciimg.isis3 import info
from sciimg.isis3 import scripting
from sciimg.isis3 import importexport
from sciimg.isis3 import _core


def normalize_vector(vec):
    l = math.sqrt(math.pow(vec[0], 2) + math.pow(vec[1], 2) + math.pow(vec[2], 2))
    if l == 0.0:
        l = 1.0
    return vec[0] / l, vec[1] / l, vec[2] / l



def calc_surface_normal(v0, v1, v2):
    v0 = np.array(v0)
    v1 = np.array(v1)
    v2 = np.array(v2)

    U = v1 - v0
    V = v2 - v1

    c = np.cross(U, V)
    n = normalize_vector(c)
    return n


def generate_sphere(min_lat, max_lat, min_lon, max_lon, lat_slices=128, lon_slices=128):
    lat_res = (max_lat - min_lat) / float(lat_slices)
    lon_res = (max_lon - min_lon) / float(lon_slices)

    vertex_list = []
    uv_list = []
    norm_list = []
    face_list = []

    for y in range(0, int(lat_slices + 1)):
        for x in range(0, int(lon_slices)):
            mx_lat = max_lat - (lat_res * y)
            mn_lon = min_lon + (lon_res * x)

            mx_lat = math.radians(mx_lat)
            mn_lon = math.radians(mn_lon)

            ul_vector = np.array(spice.srfrec(599, mn_lon, mx_lat))

            ul_uv = (x / float(lon_slices), 1.0 - y / float(lat_slices))

            norm = normalize_vector(ul_vector)

            vertex_list.append(ul_vector)
            uv_list.append(ul_uv)
            norm_list.append(norm)
    for y in range(0, int(lat_slices)):
        for x in range(0, int(lon_slices - 1)):
            ul_i = int(x + (y * lon_slices))
            ur_i = int(ul_i + 1)
            ll_i = int(ul_i + lon_slices)
            lr_i = int(ll_i + 1)

            f_ul = (ul_i, ul_i, ul_i)
            f_ll = (ll_i, ll_i, ll_i)
            f_lr = (lr_i, lr_i, lr_i)
            f_ur = (ur_i, ur_i, ur_i)
            face_list.append((f_ul, f_ll, f_lr, f_ur))

    return vertex_list, uv_list, norm_list, face_list


def rotation_matrix_to_euler_angles(R):
    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.array([x, y, z])

def radians_xyz_to_degrees_xyz(xyz):
    return np.array([math.degrees(xyz[0]), math.degrees(xyz[1]), math.degrees(xyz[2])])

def calculate_orientations(mid_time, interframe_delay, frame_number=0):
    et = mid_time
    et = et + (frame_number * interframe_delay)
    jupiter_state, lt = spice.spkpos('JUPITER', et, 'IAU_SUN', 'NONE', 'SUN')
    jupiter_state = np.array(jupiter_state)

    spacecraft_state, lt = spice.spkpos('JUNO_SPACECRAFT', et, 'IAU_JUPITER', 'NONE', 'JUPITER')
    spacecraft_state = np.array(spacecraft_state)

    m = spice.pxform("IAU_JUPITER", "J2000", et)
    jupiter_rotation = np.array(
        ((m[0][0], m[0][1], m[0][2], 0.0),
         (m[1][0], m[1][1], m[1][2], 0.0),
         (m[2][0], m[2][1], m[2][2], 0.0),
         (0.0, 0.0, 0.0, 1.0))
    )

    m = spice.pxform("JUNO_SPACECRAFT", "IAU_JUPITER", et)
    spacecraft_orientation = np.array(
        ((m[0][0], m[0][1], m[0][2], 0.0),
         (m[1][0], m[1][1], m[1][2], 0.0),
         (m[2][0], m[2][1], m[2][2], 0.0),
         (0.0, 0.0, 0.0, 1.0))
    )

    m = spice.pxform("JUNO_JUNOCAM_CUBE", "JUNO_SPACECRAFT", et)
    instrument_cube_orientation = np.array(
        ((m[0][0], m[0][1], m[0][2], 0.0),
         (m[1][0], m[1][1], m[1][2], 0.0),
         (m[2][0], m[2][1], m[2][2], 0.0),
         (0.0, 0.0, 0.0, 1.0))
    )

    m = spice.pxform("JUNO_JUNOCAM", "IAU_JUPITER", et)
    instrument_orientation = np.array(
        ((m[0][0], m[0][1], m[0][2], 0.0),
         (m[1][0], m[1][1], m[1][2], 0.0),
         (m[2][0], m[2][1], m[2][2], 0.0),
         (0.0, 0.0, 0.0, 1.0))
    )

    return spacecraft_orientation, jupiter_state, spacecraft_state, jupiter_rotation, instrument_cube_orientation, instrument_orientation



def create_obj(lbl_file, cube_file_red, output_file_path, allow_predicted=False, scalar=1.0):
    image_time = info.get_field_value(lbl_file, "IMAGE_TIME")
    interframe_delay = float(info.get_field_value(lbl_file, "INTERFRAME_DELAY")) + 0.001

    start_time = spice.str2et(info.get_field_value(lbl_file, "START_TIME")) + 0.06188
    stop_time = spice.str2et(info.get_field_value(lbl_file, "STOP_TIME")) + 0.06188
    mid_time = (start_time + stop_time) / 2.0

    num_lines = int(info.get_field_value(lbl_file, "LINES"))

    min_lat = float(scripting.getkey(cube_file_red, "MinimumLatitude", grpname="Mapping"))
    max_lat = float(scripting.getkey(cube_file_red, "MaximumLatitude", grpname="Mapping"))
    min_lon = float(scripting.getkey(cube_file_red, "MinimumLongitude", grpname="Mapping"))
    max_lon = float(scripting.getkey(cube_file_red, "MaximumLongitude", grpname="Mapping"))

    print("Image Time: ", image_time)
    print("Interframe Delay: ", interframe_delay)
    print("Start Time: ", start_time)
    print("Stop Time: ", stop_time)
    print("Middle Time: ", mid_time)
    print("Num Lines: ", num_lines)
    print("Minimum Latitude: ", min_lat)
    print("Maximum Latitude: ", max_lat)
    print("Minimum Longitude: ", min_lon)
    print("Maximum Longitude: ", max_lon)
    print("Using Predicted Kernels: ", allow_predicted)

    spacecraft_orientation, jupiter_state, spacecraft_state, jupiter_rotation, instrument_cube_orientation, instrument_orientation = calculate_orientations(mid_time, interframe_delay, frame_number=0)
    print("Spacecraft Location: ", spacecraft_state * scalar)
    rot = rotation_matrix_to_euler_angles(instrument_orientation)
    rot = radians_xyz_to_degrees_xyz(rot)
    print("JunoCam Orientation: ", rot)

    print("Generating Sphere...")
    vertex_list, uv_list, norm_list, face_list = generate_sphere(min_lat, max_lat, min_lon, max_lon, lat_slices=128, lon_slices=256)

    f = open(output_file_path, "w")
    f.write("o Sphere\n")
    for v in vertex_list:
        f.write("v %f %f %f\n"%(v[0]*scalar, v[1]*scalar, v[2]*scalar))
    for uv in uv_list:
        f.write("vt %f %f\n" % (uv[0], uv[1]))
    for n in norm_list:
        f.write("vn %f %f %f\n" % (n[0], n[1], n[2]))

    for fc in face_list:
        f.write("f")
        for il in fc:
            f.write(" %d/%d/%d"%(il[0]+1, il[1]+1, il[2]+1))
        f.write("\n")
    f.close()
    print("Done")


