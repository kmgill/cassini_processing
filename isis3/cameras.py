from isis3._core import isis_command

def spiceinit(from_cube, is_ringplane=False):
    shape = "ringplane" if is_ringplane else "system"
    s = isis_command("spiceinit", {"from": from_cube, "shape": shape})
    return s