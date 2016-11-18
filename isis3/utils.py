#!/usr/bin/python
import os
import sys
import glob

import isis3.info as info
import isis3.cassini as cissisis
import isis3.cameras as cameras
import isis3.filters as filters
import isis3.trimandmask as trimandmask
import isis3.mathandstats as mathandstats
import isis3.importexport as importexport

import isis3.cassini_iss.processing as cassproc
import isis3.voyager_iss.processing as voyproc




def output_filename(lbl_file_name):

    if cassproc.is_supported_file(lbl_file_name):
        return cassproc.output_filename(lbl_file_name)
    elif voyproc.is_supported_file(lbl_file_name):
        return voyproc.output_filename(lbl_file_name)
    else:
        raise Exception("Unsupported file type")


def output_tiff(lbl_file_name):
    out_file_base = output_filename(lbl_file_name)
    out_file_tiff = "%s.tif"%out_file_base
    return out_file_tiff

def output_cub(lbl_file_name):
    out_file_base = output_filename(lbl_file_name)
    out_file_cub = "%s.cub"%out_file_base
    return out_file_cub

def import_to_cube(lbl_file_name, to_cube):
    return cissisis.ciss2isis(lbl_file_name, to_cube)

def calibrate_cube(from_cube, to_cube):
    return cissisis.cisscal(from_cube, to_cube, units="intensity")


"""
    Simplistic method for allowing a user to just specify the first part of a file if they're (read: me) being lazy
"""
def guess_from_filename_prefix(filename):
    if os.path.exists(filename):
        return filename
    if os.path.exists("%s.LBL"%filename):
        return "%s.LBL"%filename
    if os.path.exists("%s_1.LBL"%filename):
        return "%s_1.LBL"%filename
    if os.path.exists("%s_2.LBL"%filename):
        return "%s_2.LBL"%filename


def process_pds_data_file(lbl_file_name, is_ringplane=False, is_verbose=False, skip_if_cub_exists=False):
    if cassproc.is_supported_file(lbl_file_name):
        return cassproc.process_pds_data_file(lbl_file_name, is_ringplane, is_verbose, skip_if_cub_exists)
    elif voyproc.is_supported_file(lbl_file_name):
        return voyproc.process_pds_data_file(lbl_file_name, is_ringplane, is_verbose, skip_if_cub_exists)
    else:
        raise Exception("Unsupported file type")