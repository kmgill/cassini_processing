#!/usr/bin/env python2

import sys
import os
import spiceypy as spice
import math
import numpy as np
import argparse
import glob
import json
from sciimg.isis3 import info
from sciimg.isis3 import scripting
from sciimg.isis3 import importexport
from sciimg.isis3 import _core



def print_r(*args):
    s = ' '.join(map(str, args))
    print(s)

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


def generate_sphere(min_lat, max_lat, min_lon, max_lon, lat_slices=128, lon_slices=128, target_id=599):

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

            ul_vector = np.array(spice.srfrec(target_id, mn_lon, mx_lat))

            ul_uv = (x / float(lon_slices), 1.0 - y / float(lat_slices))

            norm = normalize_vector(ul_vector)

            vertex_list.append(ul_vector)
            uv_list.append(ul_uv)
            norm_list.append(norm)

            if y < lat_slices and x < lon_slices - 1:
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

def calculate_orientations(mid_time, interframe_delay, frame_number=0, target="JUPITER"):
    et = mid_time
    et = et + (frame_number * interframe_delay)
    jupiter_state, lt = spice.spkpos(target, et, 'IAU_SUN', 'NONE', 'SUN')
    jupiter_state = np.array(jupiter_state)

    iau_target = "IAU_%s"%target

    spacecraft_state, lt = spice.spkpos('JUNO_SPACECRAFT', et, iau_target, 'NONE', target)
    spacecraft_state = np.array(spacecraft_state)

    m = spice.pxform(iau_target, "J2000", et)
    jupiter_rotation = np.array(
        ((m[0][0], m[0][1], m[0][2], 0.0),
         (m[1][0], m[1][1], m[1][2], 0.0),
         (m[2][0], m[2][1], m[2][2], 0.0),
         (0.0, 0.0, 0.0, 1.0))
    )

    m = spice.pxform("JUNO_SPACECRAFT", iau_target, et)
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

    m = spice.pxform("JUNO_JUNOCAM", iau_target, et)
    instrument_orientation = np.array(
        ((m[0][0], m[0][1], m[0][2], 0.0),
         (m[1][0], m[1][1], m[1][2], 0.0),
         (m[2][0], m[2][1], m[2][2], 0.0),
         (0.0, 0.0, 0.0, 1.0))
    )

    return spacecraft_orientation, jupiter_state, spacecraft_state, jupiter_rotation, instrument_cube_orientation, instrument_orientation


def build_model_spec_dict(lbl_file, cube_file, spacecraft_state, instrument_orientation, scalar=1.0, verbose=False):
    image_time = info.get_field_value(lbl_file, "IMAGE_TIME")
    interframe_delay = float(info.get_field_value(lbl_file, "INTERFRAME_DELAY")) + 0.001

    start_time = spice.str2et(info.get_field_value(lbl_file, "START_TIME")) + 0.06188
    stop_time = spice.str2et(info.get_field_value(lbl_file, "STOP_TIME")) + 0.06188
    mid_time = (start_time + stop_time) / 2.0
    target = info.get_field_value(lbl_file, "TARGET_NAME")

    min_lat = float(scripting.getkey(cube_file, "MinimumLatitude", grpname="Mapping"))
    max_lat = float(scripting.getkey(cube_file, "MaximumLatitude", grpname="Mapping"))
    min_lon = float(scripting.getkey(cube_file, "MinimumLongitude", grpname="Mapping"))
    max_lon = float(scripting.getkey(cube_file, "MaximumLongitude", grpname="Mapping"))

    rot = rotation_matrix_to_euler_angles(instrument_orientation)
    rot = radians_xyz_to_degrees_xyz(rot)

    if verbose:
        print_r("Target: ", target)
        print_r("Image Time: ", image_time)
        print_r("Interframe Delay: ", interframe_delay)
        print_r("Start Time: ", start_time)
        print_r("Stop Time: ", stop_time)
        print_r("Middle Time: ", mid_time)
        print_r("Minimum Latitude: ", min_lat)
        print_r("Maximum Latitude: ", max_lat)
        print_r("Minimum Longitude: ", min_lon)
        print_r("Maximum Longitude: ", max_lon)
        print_r("Scalar: ", scalar)
        print_r("Spacecraft Location: ", spacecraft_state * scalar)
        print_r("JunoCam Orientation: ", rot)

    model_spec_dict = {
        "image_time": image_time,
        "interframe_delay": interframe_delay,
        "start_time": start_time,
        "stop_time": stop_time,
        "middle_time": mid_time,
        "latitude_minimum": min_lat,
        "latitude_maximum": max_lat,
        "longitude_minimum": min_lon,
        "longitude_maximum": max_lon,
        "scalar": scalar,
        "spacecraft_location": (spacecraft_state * scalar).tolist(),
        "instrument_orientation": rot.tolist()
    }

    return model_spec_dict




def create_obj(lbl_file,
                cube_file,
                output_file_path,
                scalar=1.0,
                lat_slices=128,
                lon_slices=256,
                verbose=False,
                allow_predicted=False,
                minlat=None,
                maxlat=None,
                minlon=None,
                maxlon=None,
                limit_longitude=False):
    image_time = info.get_field_value(lbl_file, "IMAGE_TIME")

    target = info.get_field_value(lbl_file, "TARGET_NAME")

    if target == "JUPITER":
        target_id = 599
    elif target == "IO":
        target_id = 501
    elif target == "EUROPA":
        target_id = 502
    elif target == "GANYMEDE":
        target_id = 503
    elif target == "CALLISTO":
        target_id = 504
    else:
        print("ERROR: Unsupported target name found: %s"%target)
        sys.exit(1) 

    interframe_delay = float(info.get_field_value(lbl_file, "INTERFRAME_DELAY")) + 0.001

    start_time = spice.str2et(info.get_field_value(lbl_file, "START_TIME")) + 0.06188
    stop_time = spice.str2et(info.get_field_value(lbl_file, "STOP_TIME")) + 0.06188
    mid_time = (start_time + stop_time) / 2.0
    min_lat = float(scripting.getkey(cube_file, "MinimumLatitude", grpname="Mapping"))
    max_lat = float(scripting.getkey(cube_file, "MaximumLatitude", grpname="Mapping"))
    min_lon = float(scripting.getkey(cube_file, "MinimumLongitude", grpname="Mapping"))
    max_lon = float(scripting.getkey(cube_file, "MaximumLongitude", grpname="Mapping"))

    if limit_longitude is True and max_lon > 180 and max_lon - min_lon > 360.0:
        max_lon = 180

    if minlat is not None:
        min_lat = minlat
    if maxlat is not None:
        max_lat = maxlat
    if minlon is not None:
        min_lon = minlon
    if maxlon is not None:
        max_lon = maxlon

    spacecraft_orientation, jupiter_state, spacecraft_state, jupiter_rotation, instrument_cube_orientation, instrument_orientation = calculate_orientations(mid_time, interframe_delay, frame_number=0, target=target)

    model_spec_dict = build_model_spec_dict(lbl_file, cube_file, spacecraft_state, instrument_orientation, scalar=scalar,verbose=verbose)

    if verbose:
        print_r("Generating Sphere...")
    vertex_list, uv_list, norm_list, face_list = generate_sphere(min_lat, max_lat, min_lon, max_lon, lat_slices=lat_slices, lon_slices=lon_slices, target_id=target_id)

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

    if verbose:
        print_r("Done")

    return model_spec_dict


def get_image_locations(data_homes, scalar=1.0, target="JUPITER"):
    iau_target = "IAU_%s"%target

    vecs = []
    for data_home in data_homes:
        lbl_files = glob.glob('%s/*.lbl'%data_home)
        for lbl_file in lbl_files:
            image_time = spice.str2et(info.get_field_value(lbl_file, "IMAGE_TIME"))
            stop_name = info.get_field_value(lbl_file, "PRODUCT_ID")
            spacecraft_vec, lt = spice.spkpos('JUNO_SPACECRAFT', image_time, iau_target, 'NONE', target)
            stop_spec = {
                "name": stop_name,
                "vec": ((spacecraft_vec[0] * scalar), (spacecraft_vec[1] * scalar), (spacecraft_vec[2] * scalar))
            }
            vecs.append(stop_spec)
    return vecs


def get_perijove_path(begin_time, end_time, num_points=250, scalar=1.0, target="JUPITER"):
    time_sep = float(end_time - begin_time) / float(num_points - 1)
    time_iter = begin_time
    iau_target = "IAU_%s"%target

    vecs = []

    while time_iter <= end_time:
        spacecraft_vec, lt = spice.spkpos('JUNO_SPACECRAFT', time_iter, iau_target, 'NONE', target)

        vecs.append(((spacecraft_vec[0] * scalar), (spacecraft_vec[1] * scalar), (spacecraft_vec[2] * scalar)))
        time_iter += time_sep

    return vecs
