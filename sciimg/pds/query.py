import os
import sys
import requests
import json
import types


PDS_ARCHIVES_SOLR_SELECT_URL = "https://pds-imaging.jpl.nasa.gov/solr/pds_archives/select"
PDS_ATLAS_SOLR_SELECT_URL = "https://pds-imaging.jpl.nasa.gov/solr/atlas_forms/select"


class QueryFields:
    MISSION = "ATLAS_MISSION_NAME"
    INSTRUMENT = "ATLAS_INSTRUMENT_NAME"
    TARGET = "TARGET"
    FILE_NAME = "FILE_NAME"
    PRODUCT_ID = "PRODUCT_ID"
    OBSERVATION_ID = "OBSERVATION_ID"
    FILTER_NAME = "FILTER_NAME"


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




class PDSFile:

    def __init__(self, pds_solr_doc):
        self.__pds_solr_doc = pds_solr_doc

    def __getitem__(self, item):
        if item in self.__pds_solr_doc:
            return self.__pds_solr_doc[item]
        else:
            return None

    def file_name(self):
        return self["FILE_NAME"]

    def __fetch(self, url, dest_filename, verbose=False):

        if verbose:
            print "Downloading", url

        r = requests.get(url)

        if r.status_code:
            if verbose:
                print "Writing to ", dest_filename

            f = open(dest_filename, "w")
            f.write(r.content)
            f.close()

            return True
        else:
            raise Exception("Failed to fetch PDS file '%s', status code: %d"%(url, r.status_code))


    def fetch(self):
        self.__fetch(self["ATLAS_DATA_URL"], self.file_name())

        if "ATLAS_LABEL_URL" in self.__pds_solr_doc:
            self.__fetch(self["ATLAS_LABEL_URL"], os.path.basename(self["ATLAS_LABEL_URL"]))


class PDSFileList(list):

    def __init__(self, pds_solr_docs):
        list.__init__(self)
        for v in pds_solr_docs:
            self.append(v)


    def fetch_all(self):
        for f in self:
            f.fetch()


def __query_solr(url, params):


    r = requests.get(url, params=params)
    data = json.loads(r.text)

    return data


def query_fields():
    params = {
        "q": "*:*",
        "rows": 9999,
        "fl": "pds_keyword, min_value, max_value, earliest_date, latest_date",
        "wt": "json"
    }

    data = __query_solr(PDS_ATLAS_SOLR_SELECT_URL, params=params)
    return data["response"]["docs"]



def query_files(search_params={}, max_rows=10):

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
        if isinstance(value, types.ListType) or isinstance(value, types.TupleType):
            value = map(str, value)
            value = "( %s )"%" OR ".join(value)

        params["fq"].append("%s:%s"%(key, value))

    data = __query_solr(PDS_ARCHIVES_SOLR_SELECT_URL, params=params)
    docs = data["response"]["docs"]

    pds_files = []
    for doc in docs:
        pds_files.append(PDSFile(doc))

    return PDSFileList(pds_files)



if __name__ == "__main__":

    r = query_files(search_params = {
        QueryFields.MISSION: Missions.CASSINI,
        QueryFields.INSTRUMENT: "iss",
        QueryFields.OBSERVATION_ID: "ISS_131IA_IAPETUS132_PRIME",
        QueryFields.FILTER_NAME:("IR3", "GRN", "UV3")
    }, max_rows=9999)

    r.fetch_all()
