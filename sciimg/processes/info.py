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