

import sys
import unittest
from isis3 import _core
from isis3 import utils
from isis3 import info
from isis3.voyager_iss import processing
import traceback

__OUTPUT_FILE_NAME__ = "tests/data/1739S2-001_Vg2_ENCELADU_CLEAR_1981-08-26_02.35.11"

class TestIsis3Voyager(unittest.TestCase):

    LBL_FILE = "tests/data/N1489034146_2.LBL"
    IMQ_FILE = "tests/data/c4400436.imq"
    CUB_FILE = "tests/data/c4400436.cub"

    def test_spacecraft_name_imq(self):
        assert info.get_spacecraft_name(TestIsis3Voyager.IMQ_FILE) == "VOYAGER_2"

    def test_spacecraft_name_imq(self):
        assert info.get_spacecraft_name(TestIsis3Voyager.CUB_FILE) == "VOYAGER_2"

    def test_output_file_name_imq(self):
        assert processing.output_filename(TestIsis3Voyager.IMQ_FILE) == __OUTPUT_FILE_NAME__

    def test_output_file_name_cub(self):
        assert processing.output_filename(TestIsis3Voyager.CUB_FILE) == __OUTPUT_FILE_NAME__

    def test_is_supported_file_lbl(self):
        assert processing.is_supported_file(TestIsis3Voyager.LBL_FILE) is False

    def test_is_supported_file_imq(self):
        assert processing.is_supported_file(TestIsis3Voyager.IMQ_FILE) is True

    def test_is_supported_file_cub(self):
        assert processing.is_supported_file(TestIsis3Voyager.CUB_FILE) is True

    def test_get_product_id_cub(self):
        assert info.get_product_id(TestIsis3Voyager.CUB_FILE) == "1739S2-001"

    def test_get_target_imq(self):
        assert info.get_target(TestIsis3Voyager.IMQ_FILE) == "ENCELADU"

    def test_get_target_cub(self):
        assert info.get_target(TestIsis3Voyager.CUB_FILE) == "ENCELADU"

    def test_get_image_time_imq(self):
        image_time = info.get_image_time(TestIsis3Voyager.IMQ_FILE)
        assert image_time.strftime('%Y-%m-%d %H:%M:%S') == "1981-08-26 02:35:11"

    def test_get_image_time_cub(self):
        image_time = info.get_image_time(TestIsis3Voyager.CUB_FILE)
        assert image_time.strftime('%Y-%m-%d %H:%M:%S') == "1981-08-26 02:35:11"

    def test_get_num_lines_imq(self):
        assert info.get_num_lines(TestIsis3Voyager.IMQ_FILE) == 800

    def test_get_num_lines_cub(self):
        assert info.get_num_lines(TestIsis3Voyager.CUB_FILE) == 800

    def test_num_line_samples_imq(self):
        assert info.get_num_line_samples(TestIsis3Voyager.IMQ_FILE) == 800

    def test_num_line_samples_cub(self):
        assert info.get_num_line_samples(TestIsis3Voyager.CUB_FILE) == 800

    def test_get_sample_bits_imq(self):
        assert info.get_sample_bits(TestIsis3Voyager.IMQ_FILE) == 8

    def test_get_sample_bits_cub(self):
        assert info.get_sample_bits(TestIsis3Voyager.CUB_FILE) == 32

    def test_get_instrument_id_imq(self):
        assert info.get_instrument_id(TestIsis3Voyager.IMQ_FILE) == "NARROW_ANGLE_CAMERA"

    def test_get_instrument_id_cub(self):
        assert info.get_instrument_id(TestIsis3Voyager.CUB_FILE) == "NARROW_ANGLE_CAMERA"

    def test_get_filters_imq(self):
        filter1, filter2 = info.get_filters(TestIsis3Voyager.IMQ_FILE)
        assert filter1 == "CLEAR"
        assert filter2 == "CLEAR"

    def test_get_filters_cub(self):
        filter1, filter2 = info.get_filters(TestIsis3Voyager.CUB_FILE)
        assert filter1 == "CLEAR"
        assert filter2 == "CLEAR"

if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so before running tests"
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

    unittest.main()