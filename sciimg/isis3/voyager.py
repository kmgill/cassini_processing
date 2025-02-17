from sciimg.isis3._core import isis_command
import subprocess

def voy2isis(from_file, to_file):
    s = isis_command("voy2isis", {"from": from_file, "to": to_file})
    return s


def voycal(from_file, to_file):
    s = isis_command("voycal", {"from": from_file, "to": to_file})
    return s

def vdcomp(from_file, to_file):
    s = subprocess.check_output(["vdcomp", from_file, to_file])
    return s

def voyramp(from_file, to_file):
    s = subprocess.check_output(["voyramp", from_file, to_file])
    return s