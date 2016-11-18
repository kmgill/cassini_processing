
import sys
import unittest
from isis3 import info
from isis3 import _core


class TestIsis3Info(unittest.TestCase):

    LBL_FILE = "tests/data/N1489034146_2.LBL"
    CUB_FILE = "tests/data/N1489034146_ENCELADUS_CL1_IR3_2005-03-09_04.09.10.cub"
    TIF_FILE = "tests/data/N1489034146_ENCELADUS_CL1_IR3_2005-03-09_04.09.10.tif"

    def test_get_product_id_lbl(self):

        assert info.get_product_id(TestIsis3Info.LBL_FILE) == "1_N1489034146.123"

    def test_get_product_id_cub(self):
        assert info.get_product_id(TestIsis3Info.CUB_FILE) == "1_N1489034146.123"

    def test_get_target_lbl(self):
        assert info.get_target(TestIsis3Info.LBL_FILE) == "ENCELADUS"

    def test_get_target_cub(self):
        assert info.get_target(TestIsis3Info.CUB_FILE) == "ENCELADUS"

    def test_get_filters_lbl(self):
        filter1, filter2 = info.get_filters(TestIsis3Info.LBL_FILE)
        assert filter1 == "CL1"
        assert filter2 == "IR3"

    def test_get_filters_cub(self):
        filter1, filter2 = info.get_filters(TestIsis3Info.CUB_FILE)
        assert filter1 == "CL1"
        assert filter2 == "IR3"

    def test_get_image_time_lbl(self):
        image_time = info.get_image_time(TestIsis3Info.LBL_FILE)
        assert image_time.strftime('%Y-%m-%d %H:%M:%S') == "2005-03-09 04:09:10"

    def test_get_image_time_cub(self):
        image_time = info.get_image_time(TestIsis3Info.CUB_FILE)
        assert image_time.strftime('%Y-%m-%d %H:%M:%S') == "2005-03-09 04:09:10"

    def test_get_num_lines_lbl(self):
        assert info.get_num_lines(TestIsis3Info.LBL_FILE) == 1024

    def test_get_num_lines_cub(self):
        assert info.get_num_lines(TestIsis3Info.CUB_FILE) == 1024

    def test_num_line_samples_lbl(self):
        assert info.get_num_line_samples(TestIsis3Info.LBL_FILE) == 1024

    def test_num_line_samples_cub(self):
        assert info.get_num_line_samples(TestIsis3Info.CUB_FILE) == 1024

    def test_get_sample_bits_lbl(self):
        assert info.get_sample_bits(TestIsis3Info.LBL_FILE) == 8

    def test_get_sample_bits_cub(self):
        assert info.get_sample_bits(TestIsis3Info.CUB_FILE) == 32

    def test_get_instrument_id_lbl(self):
        assert info.get_instrument_id(TestIsis3Info.LBL_FILE) == "ISSNA"

    def test_get_instrument_id_cub(self):
        assert info.get_instrument_id(TestIsis3Info.CUB_FILE) == "ISSNA"

if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so before running tests"
        sys.exit(1)

    unittest.main()