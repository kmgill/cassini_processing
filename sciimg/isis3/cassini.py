
from sciimg.isis3._core import isis_command


def ciss2isis(from_file, to_file):
    s = isis_command("ciss2isis", {"from": from_file, "to": to_file})
    return s

def cisscal(from_file, to_file, units="intensity"):
    params = {
        "from": from_file,
        "to": to_file
    }
    if units is not None:
        params["units"] = units
    s = isis_command("cisscal", params)
    return s