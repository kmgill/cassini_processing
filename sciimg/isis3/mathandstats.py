from sciimg.isis3._core import isis_command
import re

def fillgap(from_cube, to_cube, interp="cubic", direction="sample"):
    s = isis_command("fillgap", {
        "from":from_cube,
        "to": to_cube,
        "interp": interp,
        "direction": direction
    })
    return s


def histeq(from_cube, to_cube, minper=0.5, maxper=99.5):
    s = isis_command("histeq", {
        "from": from_cube,
        "to": to_cube,
        "minper": minper,
        "maxper": maxper
    })
    return s


def get_data_min_max(from_cube, band=-1):

    if band >= 1:
        from_cube = "%s+%s"%(from_cube, band)

    out = isis_command("stats", {"from": from_cube})
    out = str(out).replace("\\n", "\n")
    
    min = 0
    max = 0

    pattern = re.compile(r"^ *(?P<key>[a-zA-Z0-9]*)[ =]+(?P<value>[\-A-Z0-9.e]*)")
    for line in out.split("\n"):
        match = pattern.match(line)
        if match is not None:
            key = match.group("key")
            value = match.group("value")
            if key == "Minimum":
                min = float(value)
            elif key == "Maximum":
                max = float(value)
    return min, max
