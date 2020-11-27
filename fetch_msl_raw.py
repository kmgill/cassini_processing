"""
    Fetches a set of MSL public raw images based on a simple set of search criteria.

"""

import requests
import os
import sys
import argparse
import json
from io import BytesIO


INSTRUMENTS = {
    "HAZ_FRONT" : [
        "FHAZ_RIGHT_A",
        "FHAZ_LEFT_A",
        "FHAZ_RIGHT_B",
        "FHAZ_LEFT_B"
    ],
    "HAZ_REAR" : [
        "RHAZ_RIGHT_A",
        "RHAZ_LEFT_A",
        "RHAZ_RIGHT_B",
        "RHAZ_LEFT_B"
    ],
    "NAV_LEFT" : [
        "NAV_LEFT_A",
        "NAV_LEFT_B"
    ],
    "NAV_RIGHT" : [
        "NAV_RIGHT_A",
        "NAV_RIGHT_B"
    ],
    "CHEMCAM" : [
        "CHEMCAM_RMI"
    ],
    "MARDI" : [
        "MARDI"
    ],
    "MAHLI" : [
        "MAHLI"
    ],
    "MASTCAM" : [
        "MAST_LEFT",
        "MAST_RIGHT"
    ]
}



def request(cameras=None, minsol=None, maxsol=None, num=10, page=1):

    params = {
        "order" : "sol desc,instrument_sort asc,sample_type_sort asc, date_taken desc",
        "per_page": num,
        "page": page-1,
        "condition_1": "msl:mission"
    }


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

    r = requests.get("https://mars.nasa.gov/api/v1/raw_image_items/", params=params, allow_redirects=True)

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
    print("%35s %15s %6s %27s %7s %25s"%("ID", "Instrument", "Sol", "Image Date", "Thumb", "Credit"))

def print_item(item):
    print("%35s %15s %6s %27s %7s %25s"%(item["imageid"], item["instrument"], item["sol"], item["date_taken"], item["is_thumbnail"], item["image_credit"]))

def print_results_summary(results, thumbnails=False):
    c = 0
    instruments = {}
    sols = {}
    # We count the images directly to weed out the thumbnails unless user requested those...
    for item in results["items"]:
        if item["is_thumbnail"] is False or (thumbnails is True and item["is_thumbnail"] is True):
            c = c + 1
            if not item["instrument"] in instruments:
                instruments[item["instrument"]] = 0
            instruments[item["instrument"]] = instruments[item["instrument"]] + 1

            if not item["sol"] in sols:
                sols[item["sol"]] = 0
            sols[item["sol"]] = sols[item["sol"]] + 1

    hr = "  |-----------------------------------------"
    print("")
    print(hr)
    print("  | %d images in results."%c)
    print(hr)
    for key in instruments:
        print("  | %-15s: %8d images"%(key, instruments[key]))
    print(hr)
    for key in sols:
        print("  | Sol %-11d: %8d images"%(key, sols[key]))
    print(hr)
    print("")

def print_results_list(results, thumbnails=False):
    print_list_header()
    for item in results["items"]:
        if item["is_thumbnail"] is False or (thumbnails is True and item["is_thumbnail"] is True):
            print_item(item)
    print_results_summary(results, thumbnails)


def fetch_image(item):
    image_url = item["url"]
    out_file = "%s.jpg"%item["imageid"]

    r = requests.get(image_url)

    if not r.status_code == 200:
        print("Error fetching image. HTTP status code", r.status_code, ". URL: ", image_url)
    else:
        with open(out_file, "wb") as fp:
            fp.write(r.content)


def do_fetching(results, thumbnails=False):
    print_list_header()
    for item in results["items"]:
        if item["is_thumbnail"] is False or (thumbnails is True and item["is_thumbnail"] is True):
            print_item(item)
            fetch_image(item)
    print_results_summary(results, thumbnails)

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

    results = request(camera, minsol, maxsol, num, page)
    if raw is True:
        print(json.dumps(results, indent=4))
    elif onlylist is True:
        print_results_list(results, thumbnails)
    else:
        do_fetching(results, thumbnails)
