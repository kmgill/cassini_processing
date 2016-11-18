#!/usr/bin/env python
import os
import sys
import argparse
import requests

from isis3 import utils
from isis3 import info
from isis3 import _core

JPL_SIM_URL = "http://space.jpl.nasa.gov/cgi-bin/wspace"

TARGET_IDS = {
    "CASSINI": -82,
    "SUN": 1000,
    "EARTH": 399,
    "MOON": 301,
    "JUPITER": 599,
    "IO": 501,
    "EUROPA": 502,
    "GANYMEDE": 503,
    "CALLISTO": 504,
    "SATURN": 699,
    "MIMAS": 601,
    "ENCELADUS": 602,
    "TETHYS": 603,
    "DIONE": 604,
    "RHEA": 605,
    "TITAN": 606,
    "HYPERION": 607,
    "IAPETUS": 608,
    "PHEOBE": 609,
    "PLUTO": 999
}


if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source dataset to model", required=True, type=str)
    parser.add_argument("-f", "--fov", help="Field of view (angle)", required=False, type=float)
    parser.add_argument("-p", "--pct", help="Body width as percentage of image", required=False, type=float)

    use_fov = True

    args = parser.parse_args()

    source = args.data
    fov = args.fov
    pct = args.pct

    if not os.path.exists(source):
        print "Specified dataset %s not found"%source
        sys.exit(1)

    output_path = "%s_Simulated.jpg"%utils.output_filename(source)

    image_time = info.get_image_time(source)
    target = info.get_target(source).upper()

    default_fov = 1
    camera = info.get_instrument_id(source)
    if camera == "ISSNA":
        default_fov = 0.35
    elif camera == "ISSWA":
        default_fov = 3.5

    if fov is None or fov < 1 or fov > 90:
        fov = default_fov

    if pct is not None:
        use_fov = False

    if pct is None or pct < 1 or pct > 100:
        pct = 30

    if target not in TARGET_IDS:
        print "Target '%s' is not supported by the simulator at this time"
        sys.exit(1)

    params = {
        "tbody": TARGET_IDS[target],
        "vbody": TARGET_IDS["CASSINI"],
        "year": image_time.year,
        "month": image_time.month,
        "day": image_time.day,
        "hour": image_time.hour,
        "minute": image_time.minute,
        "rfov": fov,
        "fovmul": 1 if use_fov else -1,
        "bfov": pct,
        "porbs": 1,
        "showac": 1
    }

    r = requests.get(JPL_SIM_URL, params=params)
    if r.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in r:
                f.write(chunk)
        print "Completed:", output_path
    else:
        print "Simulation Failed"
