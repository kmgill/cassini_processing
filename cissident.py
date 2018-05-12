#!/usr/bin/env python
import os
import sys
import argparse
import traceback
import signal

from sciimg.isis3 import info
from sciimg.isis3 import _core

def printInfo(lbl_file_name):
    target = info.get_target(lbl_file_name)
    filter1, filter2 = info.get_filters(lbl_file_name)
    image_time = info.get_image_time(lbl_file_name)
    num_lines = info.get_num_lines(lbl_file_name)
    num_line_samples = info.get_num_line_samples(lbl_file_name)
    sample_bits = info.get_sample_bits(lbl_file_name)

    instrument = info.get_instrument_id(lbl_file_name)
    if instrument in ("ISSNA", "NARROW_ANGLE_CAMERA"):
        camera = "Narrow"
    elif instrument in ("ISSWA", "WIDE_ANGLE_CAMERA"):
        camera = "Wide"
    else:
        camera = "NA"


    print "%25s|%10s|%10s|%22s|%5s|%5s|%4s|%8s| %s"%(target,
                                                filter1,
                                                filter2,
                                                image_time.strftime('%Y-%m-%d %H:%M:%S'),
                                                num_lines,
                                                num_line_samples,
                                                sample_bits,
                                                camera,
                                                lbl_file_name)


def signal_handler(signal, frame):
    os.kill(os.getpid(), signal.SIGUSR1)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)

    try:
        _core.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="PDS Label Files", required=False, type=str, nargs='+')
    parser.add_argument("-v", "--verbose", help="Verbose output (includes ISIS3 command output)", action="store_true")
    args = parser.parse_args()

    is_verbose = args.verbose

    data = args.data if args.data is not None else os.listdir(".")
    for file_name in data:
        if file_name[-3:].upper() in ("LBL", "CUB", "IMQ"):
            try:
                printInfo(file_name)
            except:
                if is_verbose is True:
                    traceback.print_exc(file=sys.stdout)
                print "Error processing", file_name
