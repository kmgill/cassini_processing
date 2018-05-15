

import os
import sys
import requests
import re

def __read_file_name(r):
    if not "Content-Disposition" in r.headers:
        return None

    cd = r.headers["Content-Disposition"]
    if re.match("attachment; filename=\".*\"$", cd) is not None:
        fn = re.search("(?<=\").*(?<!\")", cd).group(0)
        return fn
    else:
        return None


def fetch(url, to=None):
    r = requests.get(url=url)

    if r.status_code == 200:
        if to is None:
            to = __read_file_name(r)

        f = open(to, "w")
        f.write(r.content)
        f.close()
    else:
        raise Exception("Error downloading file. HTTP status code %s"%r.status_code)








if __name__ == "__main__":

    fetch(url="https://www.missionjuno.swri.edu/Vault/VaultDownload?VaultID=15021&t=1523298980", to="foo.zip")