import os
import sys
import types
import traceback

from sciimg.isis3 import utils
from sciimg.isis3 import info

def print_if_verbose(s, is_verbose=True):
    if is_verbose:
        print s

def process_data_file(lbl_file_name, require_target=None, require_filters=None, require_width=None, require_height=None, metadata_only=False, is_verbose=False, skip_existing=False, init_spice=True, nocleanup=False, additional_options={}):

    if isinstance(lbl_file_name, types.ListType):
        for fn in lbl_file_name:
            try:
                process_data_file(fn, require_target, require_filters, require_width, require_height, metadata_only, is_verbose, skip_existing, init_spice, nocleanup, additional_options)
            except:
                print "Error processing file '%s'"%fn
                if is_verbose:
                    traceback.print_exc(file=sys.stdout)
        return

    if lbl_file_name[-3:].upper() not in ("LBL", "BEL", "IMQ", "IMG"):  # Note: 'BEL' is for .LBL_label via atlas wget script
        print "Not a PDS label file. Skipping '%s'" % lbl_file_name
        return

    source = utils.guess_from_filename_prefix(lbl_file_name)

    return utils.process_pds_data_file(source, is_verbose=is_verbose, init_spice=init_spice, nocleanup=nocleanup, additional_options=additional_options)

