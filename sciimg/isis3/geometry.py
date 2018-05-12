from sciimg.isis3._core import isis_command


def findrx(from_cube):
    s = isis_command("findrx", {"from": from_cube})
    return s


def remrx(from_cube, to_cube, action="null", resvalid="false", sdim=9, ldim=9):

    params = {
        "from": from_cube,
        "to": to_cube,
        "action": action,
        "resvalid": resvalid,
        "SDIM": sdim,
        "LDIM": ldim
    }

    s = isis_command("remrx", params)
    return s