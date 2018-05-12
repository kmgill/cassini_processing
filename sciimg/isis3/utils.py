#!/usr/bin/python
import os
import sys
import glob

import sciimg.isis3.cassini_iss.processing as cassproc
import sciimg.isis3.voyager_iss.processing as voyproc
import sciimg.isis3.galileo_iss.processing as galproc
import sciimg.isis3.junocam.processing as jnoproc



def output_filename(lbl_file_name):

    if cassproc.is_supported_file(lbl_file_name):
        return cassproc.output_filename(lbl_file_name)
    elif voyproc.is_supported_file(lbl_file_name):
        return voyproc.output_filename(lbl_file_name)
    elif galproc.is_supported_file(lbl_file_name):
        return galproc.output_filename(lbl_file_name)
    else:
        return lbl_file_name[:-4]


def output_tiff(lbl_file_name):
    out_file_base = output_filename(lbl_file_name)
    out_file_tiff = "%s.tif"%out_file_base
    return out_file_tiff

def output_cub(lbl_file_name):
    out_file_base = output_filename(lbl_file_name)
    out_file_cub = "%s.cub"%out_file_base
    return out_file_cub


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


def process_pds_data_file(lbl_file_name,  is_verbose=False, skip_if_cub_exists=False, init_spice=True, nocleanup=False, additional_options={}):
    if cassproc.is_supported_file(lbl_file_name):
        return cassproc.process_pds_data_file(lbl_file_name, is_verbose, skip_if_cub_exists, init_spice, nocleanup, additional_options)
    elif voyproc.is_supported_file(lbl_file_name):
        return voyproc.process_pds_data_file(lbl_file_name, is_verbose, skip_if_cub_exists, init_spice, nocleanup, additional_options)
    elif galproc.is_supported_file(lbl_file_name):
        return galproc.process_pds_data_file(lbl_file_name, is_verbose, skip_if_cub_exists, init_spice, nocleanup, additional_options)
    elif jnoproc.is_supported_file(lbl_file_name):
        return jnoproc.process_pds_data_file(lbl_file_name, is_verbose, skip_if_cub_exists, init_spice, nocleanup, additional_options)
    else:
        raise Exception("Unsupported file type")

