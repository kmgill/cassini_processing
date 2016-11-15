

import unittest
from isis3 import info



class TestIsis3Info(unittest.TestCase):

    LBL_FILE = "data/N1489034146_2.LBL"
    CUB_FILE = "data/N1489034146_ENCELADUS_CL1_IR3_2005-03-09_04.09.10.cub"
    TIF_FILE = "data/N1489034146_ENCELADUS_CL1_IR3_2005-03-09_04.09.10.tif"

    def test_get_product_id_lbl(self):
        assert info.get_product_id(TestIsis3Info.LBL_FILE) == "N1489034146"

    def test_get_product_id_cub(self):
        assert info.get_product_id(TestIsis3Info.CUB_FILE) == "N1489034146"

if __name__ == "__main__":
    unittest.main()