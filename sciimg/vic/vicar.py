import os
import re
import numpy as np
from struct import *
import math

def load_vic(input_file, label_only=False):
    if not os.path.exists(input_file):
        print("Input file '%s' not found!"%input_file)
        return None, None

    f = open(input_file, "rb")
    data = f.read()
    f.close()

    # First, we need to extract the label size
    lblsize_tag = re.search('LBLSIZE=[0-9]+', data).group(0)
    LBLSIZE = int(re.search("[0-9]+", lblsize_tag).group(0))

    # Extract whole label
    label = data[0:LBLSIZE]

    # Convert raw label in to a key/value dictionary
    e = re.compile('(?:\w+)=[^ \t]+')
    value_pairs_str = e.findall(label)
    value_pairs_lst = [vp.replace("'", "").split("=") for vp in value_pairs_str]

    value_pairs = {}
    for pair in value_pairs_lst:
        value_pairs[pair[0]] = pair[1]

    if label_only is True:
        return value_pairs

    pixel_format = value_pairs["FORMAT"]
    int_format = value_pairs["INTFMT"]
    real_format = value_pairs["REALFMT"]

    unpack_format = "<f" # Will need to determine this based off of pixel_format and real_format/int_format

    NBB = int(value_pairs["NBB"])         # Number of bytes in binary prefix before each record
    NLB = int(value_pairs["NLB"])         # Number of lines (records) of binary header at the top of the file
    NL = int(value_pairs["NL"])           # Number of lines
    N1 = int(value_pairs["N1"])           # The size (in pixels) of the first dimension
    N2 = int(value_pairs["N2"])           # The size of the second dimension
    N3 = int(value_pairs["N3"])           # Size of third dimension
    NS = int(value_pairs["NS"])           # Number of samples in the image
    NB = int(value_pairs["NB"])           # Number of bands in the image
    RECSIZE = int(value_pairs["RECSIZE"]) # RECSIZE & (NBB + N1 * Pixel Size) should match
    NUMLINES = N2 * N3                    # NL & NUMLINES should match

    binary_header_size = (NLB * RECSIZE)
    binary_header_size_start = LBLSIZE
    binary_header_stop = binary_header_size + binary_header_size_start
    binary_header = data[binary_header_size_start:binary_header_stop] # Not actually doing anything with this

    pixel_matrix = np.zeros((NL, NS))

    for line_index in range(0, NUMLINES):
        line_start = binary_header_stop + (line_index * RECSIZE)
        binary_prefix_end = line_start + NBB
        line_pixels_start = binary_prefix_end
        line_end = line_start + RECSIZE

        line_binary_prefix = data[line_start:binary_prefix_end] # Not actually doing anything with this
        line_pixels_data = data[line_pixels_start:line_end]

        for s in range(0, NS):
            sample_start = s * 4 # Assuming 4 byte REAL for now...
            sample_end = sample_start + 4
            sample = line_pixels_data[sample_start:sample_end]
            sample_value = unpack(unpack_format, sample)[0]
            if math.isnan(sample_value) or sample_value == -1000.0:
                sample_value = np.nan
            pixel_matrix[line_index][s] = sample_value

    return pixel_matrix, value_pairs