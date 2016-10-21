# cassini_processing
Scripts for Cassini Imagery Processing

## Overview

This is a collection of Python and shell scripts for processing Cassini imagery from their PDS archived IMG files into either ISIS3 cube files or TIFFs. The scripts require a working and initialized installation of the USGS ISIS3 software from https://isis.astrogeology.usgs.gov/. Ensure the Cassini kernels are all installed.

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


