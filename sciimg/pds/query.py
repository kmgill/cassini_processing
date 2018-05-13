import os
import sys
import requests
import json


PDS_ARCHIVES_SOLR_SELECT_URL = "https://pds-imaging.jpl.nasa.gov/solr/pds_archives/select"
PDS_ATLAS_SOLR_SELECT_URL = "https://pds-imaging.jpl.nasa.gov/solr/atlas_forms/select"


class QueryFields:
    MISSION = "ATLAS_MISSION_NAME"
    INSTRUMENT = "ATLAS_INSTRUMENT_NAME"
    TARGET = "TARGET"


class Missions:
    MARS_ODYSSEY = "2001 mars odyssey"
    CASSINI = "cassini"
    CHANDRAYAAN_1 = "chandrayaan-1"
    CLEMENTINE = "clementine"
    GALILEO = "galileo"
    LCROSS = "lcross"
    LUNAR_ORBITER = "lunar orbiter"
    LUNAR_RECONNAISSANCE_ORBITER = "lunar reconnaissance orbiter"
    MAGELLAN = "magellan"
    MARS_EXPLORATION_ROVER = "mars exploration rover"
    MARS_GLOBAL_SURVEYOR = "mars global surveyor"
    MARS_PATHFINDER = "mars pathfinder"
    MARS_RECONNAISSANCE_ORBITER = "mars reconnaissance orbiter"
    MARS_SCIENCE_LABORATORY = "mars science laboratory"
    MESSENGER = "messenger"
    NEW_HORIZONS = "new horizons"
    PHOENIX = "phoenix"
    VIKING_LANDER = "viking lander"
    VIKING_ORBITER = "viking orbiter"
    VOYAGER = "voyager"


class Spacecraft:
    MARS_ODYSSEY = "2001 mars odyssey"
    CARL_SAGAN_MEMORIAL_STATION = "carl sagan memorial station"
    CASSINI_ORBITER = "cassini orbiter"
    CHANDRAYAAN_1 = "chandrayaan-1"
    CLEMENTINE = "clementine"
    CURIOSITY = "curiosity"
    GALILEO = "galileo"
    LCROSS = "lcross"
    LUNAR_ORBITER_1 = "lunar orbiter 1"
    LUNAR_ORBITER_2 = "lunar orbiter 2"
    LUNAR_ORBITER_3 = "lunar orbiter 3"
    LUNAR_ORBITER_4 = "lunar orbiter 4"
    LUNAR_ORBITER_5 = "lunar orbiter 5"
    LUNAR_RECONNAISSANCE_ORBITER = "lunar reconnaissance orbiter"
    MAGELLAN = "magellan"
    MARS_GLOBAL_SURVEYOR = "mars global surveyor"
    MARS_RECONNAISSANCE_ORBITER = "mars reconnaissance orbiter"
    MESSENGER = "messenger"
    NEW_HORIZONS = "new horizons"
    OPPORTUNITY = "opportunity"
    PHOENIX = "phoenix"
    SOJOURNER = "sojourner"
    SPIRIT = "spirit"
    VIKING_LANDER_1 = "viking lander 1"
    VIKING_LANDER_2 = "viking lander 2"
    VIKING_ORBITER_1 = "viking orbiter 1"
    VIKING_ORBITER_2 = "viking orbiter 2"
    VOYAGER_1 = "voyager 1"
    VOYAGER_2 = "voyager 2"


def __query_solr(url, params):


    r = requests.get(url, params=params)
    data = json.loads(r.text)

    return data


def __query_fields():
    params = {
        "q": "*:*",
        "rows": 9999,
        "fl": "pds_keyword, min_value, max_value, earliest_date, latest_date",
        "wt": "json"
    }

    data = __query_solr(PDS_ATLAS_SOLR_SELECT_URL, params=params)
    return data["response"]["docs"]



def __query_files(search_params={}, max_rows=10):

    params = {
        "q": "*:*",
        "facet": "true",
        "facet.method": "enum",
        "df": "_text_",
        "rows": max_rows,
        "sort": "START_TIME desc",
        "facet.date": "START_TIME",
        "facet.date.start": "1976-07-20T00%3A00%3A00.000Z%2FDAY",
        "facet.date.end": "2020-10-20T00%3A00%3A00.000Z%2FDAY%2B1DAY",
        "facet.date.gap": "%2B5YEAR",
        "facet.limit":-1,
        "facet.mincount": 1,
        "facet.field": "RELEVANT_DOC_FIELDS",
        "facet.field": "NO_SORT_DOC_FIELDS",
        "wt": "json",
        "fq":[]
    }

    for key in search_params:
        value = search_params[key]
        params["fq"].append("%s:%s"%(key, value))

    data = __query_solr(PDS_ARCHIVES_SOLR_SELECT_URL, params=params)
    return data["response"]["docs"]



def find(**kwargs):
    pass


def fetch(**kwargs):
    pass



if __name__ == "__main__":


    r = __query_files(search_params = {
        QueryFields.MISSION: Missions.CASSINI,
        QueryFields.INSTRUMENT: "iss",
        QueryFields.TARGET: "earth"
    }, max_rows=9999)
    print len(r)