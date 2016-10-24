# cassini_processing
Scripts for Cassini Imagery Processing

## Overview

This is a collection of Python and shell scripts for processing Cassini imagery from their PDS archived IMG files into both ISIS3 cube files and TIFFs. The scripts require a working and initialized installation of the USGS ISIS3 software from https://isis.astrogeology.usgs.gov/. Ensure the Cassini kernels are all installed.

These alone do not produce the lovely full-color images you see as the finished products. Images output by these scripts would likely require additional work in Photoshop (or your favorite photo editing software). A working knowledge of ISIS3 also comes in handy.

## Scripts

### process.py

Performs the nessessary steps for converting a PDS IMG file into a calibrated Tiff file. Tiff files are created as unsigned 16 bit grayscale. Files are output in a [PRODUCT_ID]\_[TARGET]\_[FILTER 1]\_[FILTER 2]\_[IMAGE DATE/TIME].(cub|tif) format (i.e. "N1674923569_SATURN_HAL_CL2_2011-01-28_15.45.16.tif").

```
usage: process.py [-h] -d DATA [-r] [-m] [-f FILTER [FILTER ...]] [-t TARGET]
                  [-s] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA, --data DATA  Source PDS dataset
  -r, --ringplane       Input data is of a ring plane
  -m, --metadata        Print metadata and exit
  -f FILTER [FILTER ...], --filter FILTER [FILTER ...]
                        Require filter or exit
  -t TARGET, --target TARGET
                        Require target or exit
  -s, --skipexisting    Skip processing if output already exists
  -v, --verbose         Verbose output (includes ISIS3 command output)
```



#### Examples:

Convert file 'N1674923569_1.LBL' to tiff:
```
process.py -d N1674923569_1.LBL
```

Print information about 'N1674923569_1.LBL' and exit:
```
process.py -d N1674923569_1.LBL -m
```

Convert file 'N1674923569_1.LBL' to tiff, but only if it points at Saturn:
```
process.py -d N1674923569_1.LBL -t SATURN
```

Convert file 'N1674923569_1.LBL' to tiff, but only if it utilized either CB2 or MT2 filters:
```
process.py -d N1674923569_1.LBL -f CB2 MT2
```

Convert file 'N1674923569_1.LBL' to tiff, but only if it hasn't been run before:
```
process.py -d N1674923569_1.LBL -s
```

Convert file 'N1674923569_1.LBL' to tiff using ringplane georeferencing:
```
process.py -d N1674923569_1.LBL -r
```

Convert an entire directory, limiting to Enceladus images taken in RED, GRN, and BL1:
```
find . -name "*.LBL" -exec process.py -d '{}' -t ENCELADUS -f RED GRN BL1 \;
```


### match.py
Computes min/max values for a group of cube files and exports them to tiff file with a matching stretch. This is used to ensure a correct luminance across filters. Any command line values are used to filter the files included in the processes.

#### Examples:

Convert all files in current directory:
```
match.py
```

Convert all files in current directory using RED GRN and BL1 filters (excluding other filters):
```
match.py RED GRN BL1
```

Convert all files in current directory of Titan:
```
match.py TITAN
```

Convert specified files (file names can be partial):
```
match.py W1677421231 W1677421264 W1677421297
```

### get_coiss.sh
Simple script to fetch ISS archives. Specified by archive number.

For example, to download coiss_2099.tar.gz use:
```
get_coiss.sh 2099
```


### compose_rgb.py
Process three PDS files and compose them into a single color image.

```
usage: compose_rgb.py [-h] -r RED -g GREEN -b BLUE [-m] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -r RED, --red RED     Data label for the red channel
  -g GREEN, --green GREEN
                        Data label for the green channel
  -b BLUE, --blue BLUE  Data label for the blue channel
  -m, --match           Force matching stretch values
  -v, --verbose         Verbose output (includes ISIS3 command output)
```

#### Examples:
Process three files and create a RGB output using shared stretch min/max values:
```
compose_rgb.py -r W1677421297_1.LBL -g W1677421264_1.LBL -b W1677421231_1.LBL -m
```

### cissident.py
Prints out image metadata for a list of label files

```
usage: cissident.py [-h] -d DATA [DATA ...]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA [DATA ...], --data DATA [DATA ...]
                        PDS Label Files
```

#### Examples:
```
cissident.py *.LBL
```
Prints output similar to the following, with columns as Target, Filter \#1, Filter \#2, Image Time, Width, Height, Bits per pixel, Camera, and File.
```
                    TITAN|  CL1|  CB3|   2011-04-20_12.28.45| 1024| 1024|  16|  Narrow| N1681996622_1.LBL
                    TITAN|  CL1|  MT1|   2011-04-20_12.45.45| 1024| 1024|  16|  Narrow| N1681997642_1.LBL
                    TITAN|  CB3|  CL2|   2011-04-19_11.56.10| 1024| 1024|   8|    Wide| W1681908267_1.LBL
                    TITAN|  CL1|  VIO|   2011-04-19_11.56.58| 1024| 1024|   8|    Wide| W1681908315_1.LBL
                    TITAN|  CL1|  BL1|   2011-04-19_11.57.31| 1024| 1024|   8|    Wide| W1681908348_1.LBL
                    TITAN|  CL1|  GRN|   2011-04-19_11.58.04| 1024| 1024|   8|    Wide| W1681908381_1.LBL
                    TITAN|  CL1|  RED|   2011-04-19_11.58.37| 1024| 1024|   8|    Wide| W1681908414_1.LBL
                    TITAN|  CB2|  CL2|   2011-04-19_12.13.44| 1024| 1024|   8|    Wide| W1681909321_1.LBL
```
