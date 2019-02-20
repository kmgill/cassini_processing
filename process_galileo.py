#!/usr/bin/env python2
import os
import sys
import re
import argparse
import traceback
import types
from sciimg.isis3.galileo_iss import processing

from sciimg.processes.process import process_data_file
from sciimg.isis3 import _core

def print_if_verbose(s, is_verbose=True):
    if is_verbose:
        print(s)


if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print("ISIS3 has not been initialized. Please do so. Now.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source PDS dataset", required=True, type=str, nargs='+')
    parser.add_argument("-v", "--verbose", help="Verbose output (includes ISIS3 command output)", action="store_true")
    parser.add_argument("-s", "--skipexisting", help="Skip processing if output already exists", action="store_true")
    parser.add_argument("-o", "--option", help="Mission-specific option(s)", required=False, type=str, nargs='+')
    parser.add_argument("-S", "--skipspice", help="Skip spice initialization", required=False, action="store_true")
    parser.add_argument("-n", "--nocleanup", help="Don't clean up, leave temp files", action="store_true")

    args = parser.parse_args()

    source = args.data

    skip_existing = args.skipexisting
    skip_spice = args.skipspice
    is_verbose = args.verbose
    nocleanup = args.nocleanup

    additional_options = {}

    if type(args.option) == list:
        for option in args.option:
            if re.match("^[0-9a-zA-Z]+=[0-9a-zA-Z]+$", option) is not None:
                parts = option.split("=")
                additional_options[parts[0]] = parts[1]
            else:
                print("Invalid option format:", option)
                sys.exit(1)

    try:
        for input_file in source:
            processing.process_pds_data_file(input_file, is_verbose=is_verbose, skip_if_cub_exists=skip_existing, init_spice=not skip_spice, nocleanup=nocleanup, additional_options=additional_options)
    except Exception as ex:
        print("Error processing files")
        if is_verbose:
            traceback.print_exc(file=sys.stdout)

    print_if_verbose("Done", is_verbose)


