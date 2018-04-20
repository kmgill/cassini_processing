#!/usr/bin/env python

import os
import sys
import argparse
import traceback

from isis3.junocam.utils import json_to_lbl

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Input JunoCam Metadata JSON File", required=True, type=str)

    args = parser.parse_args()

    source = args.data

    print json_to_lbl(source)
