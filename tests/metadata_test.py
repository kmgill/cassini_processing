import sys
import unittest
from isis3 import utils
from isis3 import info
from isis3 import metadata


class TestIsis3Metadata(unittest.TestCase):

    LBL_FILE = "tests/data/N1489034146_2.LBL"
    IMQ_FILE = "tests/data/c4400436.imq"
    CUB_FILE = "tests/data/c4400436.cub"

    def test_imq_file(self):
        metadata.load_pvl(TestIsis3Metadata.IMQ_FILE, verbose=True)
        metadata.load_pvl(TestIsis3Metadata.IMQ_FILE, verbose=True)

if __name__ == "__main__":

    try:
        utils.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so before running tests"
        sys.exit(1)

    unittest.main()