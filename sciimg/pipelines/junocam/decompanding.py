import numpy as np


class CompandingTableEnum:
    """
    Check SAMPLE_BIT_MODE_ID in PDS metadata (LBL) for appropriate companding table to use for a given image
    """
    SQROOT = "SQROOT"
    LIN1 = "LIN1"
    LIN8 = "LIN8"
    LIN16 = "LIN16"


"""
Reference 

"Software Interface Specification JunoCam Standard Data Products"
M. Caplinger
Malin Space Science Systems, Inc.

"""


SQROOT = np.array((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                   16, 17, 18, 19, 20, 21, 22, 23, 25, 27, 29, 31, 33, 35, 37, 39,
                   41, 43, 45, 47, 49, 51, 53, 55, 57, 59, 61, 63, 67, 71, 75,
                   79, 83, 87, 91, 95, 99, 103, 107, 111, 115, 119, 123, 127, 131,
                   135, 139, 143, 147, 151, 155, 159, 163, 167, 171, 175, 179,
                   183, 187, 191, 195, 199, 203, 207, 211, 215, 219, 223, 227,
                   231, 235, 239, 243, 247, 255, 263, 271, 279, 287, 295, 303,
                   311, 319, 327, 335, 343, 351, 359, 367, 375, 383, 391, 399,
                   407, 415, 423, 431, 439, 447, 455, 463, 471, 479, 487, 495,
                   503, 511, 519, 527, 535, 543, 551, 559, 567, 575, 583, 591,
                   599, 607, 615, 623, 631, 639, 647, 655, 663, 671, 679, 687,
                   695, 703, 711, 719, 727, 735, 743, 751, 759, 767, 775, 783,
                   791, 799, 807, 815, 823, 831, 839, 847, 855, 863, 871, 879,
                   887, 895, 903, 911, 919, 927, 935, 943, 951, 959, 967, 975,
                   983, 991, 999, 1007, 1023, 1039, 1055, 1071, 1087, 1103, 1119,
                   1135, 1151, 1167, 1183, 1199, 1215, 1231, 1247, 1263, 1279,
                   1295, 1311, 1327, 1343, 1359, 1375, 1391, 1407, 1439, 1471,
                   1503, 1535, 1567, 1599, 1631, 1663, 1695, 1727, 1759, 1791,
                   1823, 1855, 1887, 1919, 1951, 1983, 2015, 2047, 2079, 2111,
                   2143, 2175, 2207, 2239, 2271, 2303, 2335, 2367, 2399, 2431,
                   2463, 2495, 2527, 2559, 2591, 2623, 2655, 2687, 2719, 2751,
                   2783, 2815, 2847, 2879), dtype=np.float32)

LIN1 = np.array((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
                 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
                 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
                 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
                 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95,
                 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
                 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127,
                 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143,
                 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
                 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175,
                 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191,
                 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207,
                 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223,
                 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
                 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255),
                dtype=np.float32)

LIN8 = np.array((0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96,
                 104, 112, 120, 128, 136, 144, 152, 160, 168, 176, 184, 192, 200,
                 208, 216, 224, 232, 240, 248, 256, 264, 272, 280, 288, 296, 304,
                 312, 320, 328, 336, 344, 352, 360, 368, 376, 384, 392, 400, 408,
                 416, 424, 432, 440, 448, 456, 464, 472, 480, 488, 496, 504, 512,
                 520, 528, 536, 544, 552, 560, 568, 576, 584, 592, 600, 608, 616,
                 624, 632, 640, 648, 656, 664, 672, 680, 688, 696, 704, 712, 720,
                 728, 736, 744, 752, 760, 768, 776, 784, 792, 800, 808, 816, 824,
                 832, 840, 848, 856, 864, 872, 880, 888, 896, 904, 912, 920, 928,
                 936, 944, 952, 960, 968, 976, 984, 992, 1000, 1008, 1016, 1024, 1032,
                 1040, 1048, 1056, 1064, 1072, 1080, 1088, 1096, 1104, 1112, 1120, 1128, 1136,
                 1144, 1152, 1160, 1168, 1176, 1184, 1192, 1200, 1208, 1216, 1224, 1232, 1240,
                 1248, 1256, 1264, 1272, 1280, 1288, 1296, 1304, 1312, 1320, 1328, 1336, 1344,
                 1352, 1360, 1368, 1376, 1384, 1392, 1400, 1408, 1416, 1424, 1432, 1440, 1448,
                 1456, 1464, 1472, 1480, 1488, 1496, 1504, 1512, 1520, 1528, 1536, 1544, 1552,
                 1560, 1568, 1576, 1584, 1592, 1600, 1608, 1616, 1624, 1632, 1640, 1648, 1656,
                 1664, 1672, 1680, 1688, 1696, 1704, 1712, 1720, 1728, 1736, 1744, 1752, 1760,
                 1768, 1776, 1784, 1792, 1800, 1808, 1816, 1824, 1832, 1840, 1848, 1856, 1864,
                 1872, 1880, 1888, 1896, 1904, 1912, 1920, 1928, 1936, 1944, 1952, 1960, 1968,
                 1976, 1984, 1992, 2000, 2008, 2016, 2024, 2032, 2040), dtype=np.float32)

LIN16 = np.array((0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192,
                  208, 224, 240, 256, 272, 288, 304, 320, 336, 352, 368, 384, 400,
                  416, 432, 448, 464, 480, 496, 512, 528, 544, 560, 576, 592, 608,
                  624, 640, 656, 672, 688, 704, 720, 736, 752, 768, 784, 800, 816,
                  832, 848, 864, 880, 896, 912, 928, 944, 960, 976, 992, 1008, 1024,
                  1040, 1056, 1072, 1088, 1104, 1120, 1136, 1152, 1168, 1184, 1200, 1216, 1232,
                  1248, 1264, 1280, 1296, 1312, 1328, 1344, 1360, 1376, 1392, 1408, 1424, 1440,
                  1456, 1472, 1488, 1504, 1520, 1536, 1552, 1568, 1584, 1600, 1616, 1632, 1648,
                  1664, 1680, 1696, 1712, 1728, 1744, 1760, 1776, 1792, 1808, 1824, 1840, 1856,
                  1872, 1888, 1904, 1920, 1936, 1952, 1968, 1984, 2000, 2016, 2032, 2048, 2064,
                  2080, 2096, 2112, 2128, 2144, 2160, 2176, 2192, 2208, 2224, 2240, 2256, 2272,
                  2288, 2304, 2320, 2336, 2352, 2368, 2384, 2400, 2416, 2432, 2448, 2464, 2480,
                  2496, 2512, 2528, 2544, 2560, 2576, 2592, 2608, 2624, 2640, 2656, 2672, 2688,
                  2704, 2720, 2736, 2752, 2768, 2784, 2800, 2816, 2832, 2848, 2864, 2880, 2896,
                  2912, 2928, 2944, 2960, 2976, 2992, 3008, 3024, 3040, 3056, 3072, 3088, 3104,
                  3120, 3136, 3152, 3168, 3184, 3200, 3216, 3232, 3248, 3264, 3280, 3296, 3312,
                  3328, 3344, 3360, 3376, 3392, 3408, 3424, 3440, 3456, 3472, 3488, 3504, 3520,
                  3536, 3552, 3568, 3584, 3600, 3616, 3632, 3648, 3664, 3680, 3696, 3712, 3728,
                  3744, 3760, 3776, 3792, 3808, 3824, 3840, 3856, 3872, 3888, 3904, 3920, 3936,
                  3952, 3968, 3984, 4000, 4016, 4032, 4048, 4064, 4080), dtype=np.float32)


def decompand(img_data, table=CompandingTableEnum.SQROOT, verbose=False):
    if table == CompandingTableEnum.SQROOT:
        ctable = SQROOT
    elif table == CompandingTableEnum.LIN1:
        ctable = LIN1
    elif table == CompandingTableEnum.LIN8:
        ctable = LIN8
    elif table == CompandingTableEnum.LIN16:
        ctable = LIN16
    else:
        raise Exception("Invalid companding table specified")

    for a in range(0, len(img_data)):
        for b in range(0, len(img_data[a])):
            img_data[a][b] = ctable[int(round(img_data[a][b]))]

    return img_data