#!/usr/bin/env python
"""
    Fetches a set of Mars2020 public raw images based on a simple set of search criteria.

"""

import requests
import os
import sys
import argparse
import json
from io import BytesIO
import ast

INSTRUMENTS = {
    "HAZ_FRONT" : [
        "FRONT_HAZCAM_LEFT_A",
        "FRONT_HAZCAM_LEFT_B",
        "FRONT_HAZCAM_RIGHT_A",
        "FRONT_HAZCAM_RIGHT_B",
    ],
    "SUPERCAM" : [
        "SUPERCAM_RMI"
    ],
    "HAZ_REAR" : [
        "REAR_HAZCAM_LEFT",
        "REAR_HAZCAM_RIGHT"
    ],
    "NAVCAM" : [
        "NAVCAM_LEFT",
        "NAVCAM_RIGHT"
    ],
    "MASTCAM" : [
        "MCZ_LEFT",
        "MCZ_RIGHT"
    ],
    "EDLCAM" : [
        "EDL_DDCAM",
        "EDL_PUCAM1",
        "EDL_PUCAM2",
        "EDL_RUCAM",
        "EDL_RDCAM",
        "LCAM"
    ],
    "WATSON" : [
        "SHERLOC_WATSON"
    ]
}



def request(cameras=None, minsol=None, maxsol=None, num=10, page=1, only_movie=False, thumbnails=False):

    params = {
        "feed": "raw_images",
        "category": "mars2020",
        "feedtype": "json",
        "num": num,
        "page": page-1,
        "order": "sol desc"
    }

    if thumbnails is True:
        params["extended"] = "sample_type::thumbnail,"
    elif only_movie is True:
        params["extended"] = "sample_type::full,product_id::ecv,"
    else:
        params["extended"] = "sample_type::full,"

    if cameras is not None:
        usecams = []
        for cam in cameras:
            if cam in INSTRUMENTS:
                for c in INSTRUMENTS[cam]:
                    usecams.append(c)
            else:
                usecams.append(cam)
        usecams = "|".join(usecams)
        params["search"] = usecams

    if minsol is not None:
        params["condition_2"] = "%d:sol:gte"%minsol
    if maxsol is not None:
        params["condition_3"] = "%d:sol:lte"%maxsol

    r = requests.get("https://mars.nasa.gov/rss/api/", params=params, allow_redirects=True)

    if not r.status_code == 200:
        print("Error fetching search results. HTTP status code", r.status_code)
        sys.exit(0)

    return r.json()


def build_choices_list():
    choices = []
    for a in INSTRUMENTS:
        choices.append(a)
        for b in INSTRUMENTS[a]:
            choices.append(b)

    return choices

def print_list_header():
    print("%54s %25s %6s %27s %27s %6s %6s %6s %6s %7s"%("ID", "Instrument", "Sol", "Image Date (UTC)", "Image Date (Mars)", "Site", "Drive", "Width", "Height", "Thumb"))

def print_item(item):
    subframe_rect = ast.literal_eval(item["extended"]["dimension"])
    print("%54s %25s %6s %27s %27s %6s %6s %6s %6s %7s"%(item["imageid"],
                                                    item["camera"]["instrument"],
                                                    item["sol"],
                                                    item["date_taken_utc"],
                                                    item["date_taken_mars"],
                                                    item["site"],
                                                    item["drive"],
                                                    subframe_rect[0],
                                                    subframe_rect[1],
                                                    item["sample_type"] == "Thumbnail"))

def print_results_summary(results, thumbnails=False, seqid=None):
    c = 0
    instruments = {}
    sols = {}
    # We count the images directly to weed out the thumbnails unless user requested those...
    for item in results["images"]:
        if (item["sample_type"] != "Thumbnail" or (thumbnails is True and item["sample_type"] == "Thumbnail")) and \
            (seqid is None or (seqid in item["imageid"])):
            c = c + 1
            if not item["camera"]["instrument"] in instruments:
                instruments[item["camera"]["instrument"]] = 0
            instruments[item["camera"]["instrument"]] = instruments[item["camera"]["instrument"]] + 1

            if not item["sol"] in sols:
                sols[item["sol"]] = 0
            sols[item["sol"]] = sols[item["sol"]] + 1

    hr = "  |----------------------------------------------"
    print("")
    print(hr)
    print("  | %d images in results."%c)
    print(hr)
    for key in instruments:
        print("  | %-25s: %8d images"%(key, instruments[key]))
    print(hr)
    for key in sols:
        print("  | Sol %-11d: %8d images"%(key, sols[key]))
    print(hr)
    print("")

def print_results_list(results, thumbnails=False, seqid=None):
    print_list_header()
    for item in results["images"]:
        if (item["sample_type"] != "Thumbnail" or (thumbnails is True and item["sample_type"] == "Thumbnail")) and \
            (seqid is None or (seqid in item["imageid"])):
            print_item(item)
    print_results_summary(results, thumbnails, seqid)


def fetch_image(item):
    image_url = item["image_files"]["full_res"]
    out_file = "%s.png"%item["imageid"]

    r = requests.get(image_url)

    if not r.status_code == 200:
        print("Error fetching image. HTTP status code", r.status_code, ". URL: ", image_url)
    else:
        with open(out_file, "wb") as fp:
            fp.write(r.content)


def do_fetching(results, thumbnails=False, seqid=None):
    print_list_header()
    for item in results["images"]:
        if (item["sample_type"] != "Thumbnail" or (thumbnails is True and item["sample_type"] == "Thumbnail")) and \
            (seqid is None or (seqid in item["imageid"])):
            print_item(item)
            fetch_image(item)
    print_results_summary(results, thumbnails, seqid)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--camera", help="MSL Camera Instrument(s)", required=None, default=None, type=str, nargs='+', choices=build_choices_list())
    parser.add_argument("-s", "--sol", help="Mission Sol", required=False, type=int)
    parser.add_argument("-m", "--minsol", help="Starting Mission Sol", required=False, type=int)
    parser.add_argument("-M", "--maxsol", help="Ending Mission Sol", required=False, type=int)
    parser.add_argument("-l", "--list", help="Don't download, only list results", action="store_true")
    parser.add_argument("-r", "--raw", help="Print raw JSON response", action="store_true")
    parser.add_argument("-t", "--thumbnails", help="Download thumbnails in the results", action="store_true")
    parser.add_argument("-n", "--num", help="Max number of results", required=False, type=int, default=100)
    parser.add_argument("-p", "--page", help="Results page (starts at 1)", required=False, type=int, default=1)
    parser.add_argument("-S", "--seqid", help="Specific sequence id", required=False, type=str, default=None)
    parser.add_argument("-e", "--movie", help="Only movie frames", action="store_true")

    args = parser.parse_args()
    camera = args.camera
    sol = args.sol
    minsol = args.minsol
    maxsol = args.maxsol
    onlylist = args.list
    num = args.num
    page = args.page
    raw = args.raw
    thumbnails = args.thumbnails
    only_movie = args.movie

    # Looks like we can't filter by seqid on the web query, even as a
    # subscript of imageid. Until we find a way, we'll have to do
    # the limiting in the print/download methods
    seqid = args.seqid

    if sol is not None:
        assert minsol is None and maxsol is None
        minsol = sol
        maxsol = sol
    elif minsol is not None or maxsol is not None:
        assert sol is None

    if raw is True:
        assert onlylist is False
    elif onlylist is True:
        assert raw is False

    results = request(camera, minsol, maxsol, num, page, only_movie, thumbnails)
    if raw is True:
        print(json.dumps(results, indent=4))
    elif onlylist is True:
        print_results_list(results, thumbnails, seqid)
    else:
        do_fetching(results, thumbnails, seqid)
