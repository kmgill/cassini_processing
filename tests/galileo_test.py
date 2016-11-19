
import sys
import unittest
from isis3 import utils
from isis3 import info
from isis3.galileo_iss import processing

__OUTPUT_FILE_NAME__ = "tests/data/25I0045_IO_GREEN_1999-11-26_04.53.00"

class TestIsis3Galileo(unittest.TestCase):

    IMG_FILE = "tests/data/6300r.img"
    LBL_FILE = "tests/data/6300r.lbl"
    CUB_FILE = "tests/data/6300R_IO_GREEN_1999-11-26.cub"
    TIF_FILE = "tests/data/6300R_IO_GREEN_1999-11-26.TIF"

    CASSINI_LBL_FILE = "tests/data/N1489034146_2.LBL"
    VOYAGER_IMQ_FILE = "tests/data/c4400436.imq"
    VOYAGER_CUB_FILE = "tests/data/c4400436.cub"

    def test_output_file_name_lbl(self):
        assert processing.output_filename(TestIsis3Galileo.LBL_FILE) == __OUTPUT_FILE_NAME__

    def test_output_file_name_cub(self):
        assert processing.output_filename(TestIsis3Galileo.CUB_FILE) == __OUTPUT_FILE_NAME__

    def test_is_supported_file_cassini_lbl(self):
        assert processing.is_supported_file(TestIsis3Galileo.CASSINI_LBL_FILE) is False

    def test_is_supported_file_voyager_imq(self):
        assert processing.is_supported_file(TestIsis3Galileo.VOYAGER_IMQ_FILE) is False

    def test_is_supported_file_voyager_cub(self):
        assert processing.is_supported_file(TestIsis3Galileo.VOYAGER_CUB_FILE) is False

    def test_is_supported_file_lbl(self):
        assert processing.is_supported_file(TestIsis3Galileo.LBL_FILE) is True

    def test_is_supported_file_cub(self):
        assert processing.is_supported_file(TestIsis3Galileo.CUB_FILE) is True

    def test_get_product_id_lbl(self):
        assert info.get_product_id(TestIsis3Galileo.LBL_FILE) == "25I0045"

    def test_get_product_id_cub(self):
        assert info.get_product_id(TestIsis3Galileo.CUB_FILE) == "25I0045"

    def test_get_target_lbl(self):
        assert info.get_target(TestIsis3Galileo.LBL_FILE) == "IO"

    def test_get_target_cub(self):
        assert info.get_target(TestIsis3Galileo.CUB_FILE) == "IO"

    def test_get_image_time_lbl(self):
        image_time = info.get_image_time(TestIsis3Galileo.LBL_FILE)
        assert image_time.strftime('%Y-%m-%d %H:%M:%S') == "1999-11-26 04:53:00"

    def test_get_image_time_cub(self):
        image_time = info.get_image_time(TestIsis3Galileo.CUB_FILE)
        assert image_time.strftime('%Y-%m-%d %H:%M:%S') == "1999-11-26 04:53:00"

    def test_get_num_lines_lbl(self):
        assert info.get_num_lines(TestIsis3Galileo.LBL_FILE) == 800

    def test_get_num_lines_cub(self):
        assert info.get_num_lines(TestIsis3Galileo.CUB_FILE) == 800

    def test_num_line_samples_lbl(self):
        assert info.get_num_line_samples(TestIsis3Galileo.LBL_FILE) == 800

    def test_num_line_samples_cub(self):
        assert info.get_num_line_samples(TestIsis3Galileo.CUB_FILE) == 800

    def test_get_sample_bits_lbl(self):
        assert info.get_sample_bits(TestIsis3Galileo.LBL_FILE) == 8

    def test_get_sample_bits_cub(self):
        assert info.get_sample_bits(TestIsis3Galileo.CUB_FILE) == 32

    def test_get_instrument_id_lbl(self):
        assert info.get_instrument_id(TestIsis3Galileo.LBL_FILE) == "SOLID STATE IMAGING SYSTEM"

    def test_get_instrument_id_cub(self):
        assert info.get_instrument_id(TestIsis3Galileo.CUB_FILE) == "SOLID STATE IMAGING SYSTEM"

    def test_get_filters_lbl(self):
        filter1, filter2 = info.get_filters(TestIsis3Galileo.LBL_FILE)
        assert filter1 == "GREEN"
        assert filter2 == "GREEN"

    def test_get_filters_cub(self):
        filter1, filter2 = info.get_filters(TestIsis3Galileo.CUB_FILE)
        assert filter1 == "GREEN"
        assert filter2 == "GREEN"


if __name__ == "__main__":

    try:
        utils.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so before running tests"
        sys.exit(1)

    unittest.main()