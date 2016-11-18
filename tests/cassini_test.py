
import sys
import unittest
from isis3 import utils
from isis3 import info
from isis3.cassini_iss import processing


__OUTPUT_FILE_NAME__ = "tests/data/N1489034146_ENCELADUS_CL1_IR3_2005-03-09_04.09.10"

class TestIsis3Cassini(unittest.TestCase):

    IMQ_FILE = "tests/data/c4400436.imq"
    LBL_FILE = "tests/data/N1489034146_2.LBL"
    CUB_FILE = "tests/data/N1489034146_ENCELADUS_CL1_IR3_2005-03-09_04.09.10.cub"
    TIF_FILE = "tests/data/N1489034146_ENCELADUS_CL1_IR3_2005-03-09_04.09.10.tif"

    def test_output_file_name_lbl(self):
        assert processing.output_filename(TestIsis3Cassini.LBL_FILE) == __OUTPUT_FILE_NAME__

    def test_output_file_name_cub(self):
        assert processing.output_filename(TestIsis3Cassini.CUB_FILE) == __OUTPUT_FILE_NAME__

    def test_is_supported_file_imq(self):
        assert processing.is_supported_file(TestIsis3Cassini.IMQ_FILE) is False

    def test_is_supported_file_lbl(self):
        assert processing.is_supported_file(TestIsis3Cassini.LBL_FILE) is True

    def test_is_supported_file_cub(self):
        assert processing.is_supported_file(TestIsis3Cassini.CUB_FILE) is True
