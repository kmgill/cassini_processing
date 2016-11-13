from isis3._core import isis_command


def noisefilter(from_cube, to_cube, toldef="stddev", tolmin=2.5, tolmax=2.5, replace="null", samples=5, lines=5):
    s = isis_command("noisefilter", {
        "from": from_cube,
        "to": to_cube,
        "toldef": toldef,
        "tolmin": tolmin,
        "tolmax": tolmax,
        "replace": replace,
        "samples": samples,
        "lines": lines
    })
    return s


def lowpass(from_cube, to_cube, samples=5, lines=3, filter="outside", null="yes", hrs="no", his="no", lrs="no", replacement="center"):
    s = isis_command("lowpass", {
        "from": from_cube,
        "to": to_cube,
        "samples": samples,
        "lines": lines,
        "filter": filter,
        "null": null,
        "hrs": hrs,
        "his": his,
        "lrs": lrs,
        "replacement": replacement
    })
    return s

