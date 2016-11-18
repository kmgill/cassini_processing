import sys
import unittest
from isis3 import utils


class TestIsis3Utils(unittest.TestCase):

    LBL_FILE = "tests/data/N1489034146_2.LBL"
    CUB_FILE = "tests/data/N1489034146_ENCELADUS_CL1_IR3_2005-03-09_04.09.10.cub"
    TIF_FILE = "tests/data/N1489034146_ENCELADUS_CL1_IR3_2005-03-09_04.09.10.tif"

    def test_output_filename_from_label(self):
        assert utils.output_filename(TestIsis3Utils.LBL_FILE) == "tests/data/N1489034146_ENCELADUS_CL1_IR3_2005-03-09_04.09.10"

    def test_output_tiff_from_label(self):
        assert utils.output_tiff(TestIsis3Utils.LBL_FILE) == TestIsis3Utils.TIF_FILE

    def test_output_cub_from_label(self):
        assert utils.output_cub(TestIsis3Utils.LBL_FILE) == TestIsis3Utils.CUB_FILE

    def test_guess_from_filename_prefix(self):
        assert utils.guess_from_filename_prefix(TestIsis3Utils.LBL_FILE[:-4]) == TestIsis3Utils.LBL_FILE
        assert utils.guess_from_filename_prefix(TestIsis3Utils.LBL_FILE[:-6]) == TestIsis3Utils.LBL_FILE

if __name__ == "__main__":

    try:
        utils.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so before running tests"
        sys.exit(1)

    unittest.main()