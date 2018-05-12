#!/usr/bin/env python
import os
import sys
import argparse
import traceback
import signal

from sciimg.isis3 import info
from sciimg.isis3 import _core

from sciimg.processes.info import printInfo

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
