from sciimg.isis3._core import isis_command


class Priority:
    ONTOP = "ONTOP"
    BENEATH = "BENEATH"
    BAND = "BAND"
    AVERAGE = "AVERAGE"


def automos(from_list, to_file, priority=Priority.ONTOP):

    params = {
        "fromlist": from_list,
        "mosaic": to_file,
        "priority": priority
    }

    s = isis_command("automos", params)
    return s
