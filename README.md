# Cassini, Voyager, & Galileo Image Processing
Scripts and utilities for processing Juno, Cassini, Voyager, & Galileo imagery from NASA PDS archived data. 

## Overview

This is a collection of Python and shell scripts for processing Cassini and Voyager imagery from their PDS archived IMG and IMQ files into both ISIS3 cube files and TIFFs. The scripts require a working and initialized installation of the USGS ISIS3 software from https://isis.astrogeology.usgs.gov/. Ensure the ISIS3 mission kernels are all installed.

These alone do not produce the lovely full-color images you see as the finished products. Images output by these scripts would likely require additional work in Photoshop (or your favorite photo editing software). A working knowledge of ISIS3 also comes in handy.

## Mission-Specific Documentation

 * [JunoCam Processing](https://github.com/kmgill/cassini_processing/blob/master/doc/JunoCamProcessing.md)

## Scripts

### initcass.sh

Performs initalization of ISIS3 and adds these scripts to your shell's search path. **_EDIT this file before using so it reflects your installation environment._** 

To Use, 'script' it:
```
. /path/to/initcass.sh
```

### process.py

Performs the nessessary steps for converting a PDS IMG file into a calibrated Tiff file. Tiff files are created as unsigned 16 bit grayscale. Files are output in a [PRODUCT_ID]\_[TARGET]\_[FILTER 1]\_[FILTER 2]\_[IMAGE DATE/TIME].(cub|tif) format (i.e. "N1674923569_SATURN_HAL_CL2_2011-01-28_15.45.16.tif").

```
usage: process.py [-h] -d DATA [DATA ...] [-m] [-f FILTER [FILTER ...]]
                  [-t TARGET] [-s] [-v] [-w WIDTH [WIDTH ...]]
                  [-H HEIGHT [HEIGHT ...]] [-S] [-p PROJECTION] [-n]
                  [-o OPTION [OPTION ...]]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA [DATA ...], --data DATA [DATA ...]
                        Source PDS dataset
  -m, --metadata        Print metadata and exit
  -f FILTER [FILTER ...], --filter FILTER [FILTER ...]
                        Require filter or exit
  -t TARGET, --target TARGET
                        Require target or exit
  -s, --skipexisting    Skip processing if output already exists
  -v, --verbose         Verbose output (includes ISIS3 command output)
  -w WIDTH [WIDTH ...], --width WIDTH [WIDTH ...]
                        Require width or exit
  -H HEIGHT [HEIGHT ...], --height HEIGHT [HEIGHT ...]
                        Require height or exit
  -S, --skipspice       Skip spice initialization
  -p PROJECTION, --projection PROJECTION
                        Map projection (Juno)
  -n, --nocleanup       Don't clean up, leave temp files
  -o OPTION [OPTION ...], --option OPTION [OPTION ...]
                        Mission-specific option(s)
```

#### Mission-Specific Options:
* Cassini:

   `ringplane=true|false` - Optionally treats an image using ring-plane geometry
   
* Juno:

   `vt=n` - Apply vertical (top & bottom) trimming on each framelet where `n` is the number of pixels trimmed.
   `histeq=true|false` - Optionally run histogram equalization on the output images

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
process.py -d *.LBL -t ENCELADUS -f RED GRN BL
```

**Note:** The Voyager process includes automatically addressing Reseaus using the ISIS3 findrx and remrx commands. These are imperfect, but still improve the image. 

Without reseau removal: 

<img src="https://raw.githubusercontent.com/kmgill/cassini_processing/master/docs/images/c4411057.jpg" width="400">

With reseau removal:

<img src="https://raw.githubusercontent.com/kmgill/cassini_processing/master/docs/images/c4411057-nullrx.jpg" width="400">


### match.py
Computes min/max values for a group of cube files and exports them to tiff file with a matching stretch. This is used to ensure a correct luminance across filters. 

```
usage: match.py [-h] -d DATA [DATA ...] [-f FILTERS [FILTERS ...]]
                [-t TARGETS [TARGETS ...]]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA [DATA ...], --data DATA [DATA ...]
                        Source PDS dataset(s)
  -f FILTERS [FILTERS ...], --filters FILTERS [FILTERS ...]
                        Require filter(s) or exit
  -t TARGETS [TARGETS ...], --targets TARGETS [TARGETS ...]
                        Require target(s) or exit
```

#### Output Example:
Once mosaicked, brightness matched images will blend without requiring post-processing adjustments.
<img src="https://raw.githubusercontent.com/kmgill/cassini_processing/master/docs/images/match-examples.jpg" width="400">

#### Examples:

Process all the cubes in the working directory:
```
match.py -d *.cub
```
Process a set of specific files:
```
match.py -d N1684428714_TITAN_CL1_GRN_2011-05-18_16.03.21.cub N1684686374_TITAN_RED_CL2_2011-05-21_15.37.40.cub N1684686408_TITAN_CL1_GRN_2011-05-21_15.38.14.cub 
```

Process all the cubes in the working directory that target Titan:
```
match.py -d *.cub -t titan
```

Process all the cubes in the working directory that target Titan and use RED/GRN/BL1 filters:
```
match.py -d *.cub -t titan -f RED GRN BL1
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
compose_rgb.py -r N1713218719_1.LBL -g N1713218686_1.LBL -b N1713218653_1.LBL -m
```

Output:
<img src="https://raw.githubusercontent.com/kmgill/cassini_processing/master/docs/images/compose_rgb-matched.jpg" width="400">

Process three files and create a RGB output, each channel independently stretched:
```
compose_rgb.py -r N1713218719_1.LBL -g N1713218686_1.LBL -b N1713218653_1.LBL
```

Output:
<img src="https://raw.githubusercontent.com/kmgill/cassini_processing/master/docs/images/compose_rgb-unmatched.jpg" width="400">


### cissident.py
Prints out image metadata for a list of label files

```
usage: cissident.py [-h] [-d DATA [DATA ...]]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA [DATA ...], --data DATA [DATA ...]
                        PDS Label Files
```

#### Examples:
```
cissident.py -d *.LBL
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

### getmodel.py
Downloads a simulated view of the specified image from http://space.jpl.nasa.gov/

```
usage: getmodel.py [-h] -d DATA [-f FOV] [-p PCT]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA, --data DATA  Source dataset to model
  -f FOV, --fov FOV     Field of view (angle)
  -p PCT, --pct PCT     Body width as percentage of image
```

#### Examples:
Fetch a simulated image for a specified dataset with defaults selected:
```
getmodel.py -d W1692470929_1.LBL
```
Original Image:
<img src="https://raw.githubusercontent.com/kmgill/cassini_processing/master/docs/images/getmodel-actual.jpg" width="400">

Modeled Image:
<img src="https://raw.githubusercontent.com/kmgill/cassini_processing/master/docs/images/getmodel-model.jpg" width="400">

Fetch a simluated image using a custom field of view (degrees):
```
getmodel.py -d W1692470929_1.LBL -f 40
```

### cub2tiff.py
Converts a Cassini ISS cube file into a 16 bit (unsigned integer) tiff. 

```
usage: cub2tiff.py [-h] -d DATA [DATA ...]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA [DATA ...], --data DATA [DATA ...]
                        Source cube file
```

### project.py
Converts an input cube from the original camera geometry to a map projected format.
```
usage: project.py [-h] -d DATA [DATA ...] [-p PROJECTION] [-m MAP]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA [DATA ...], --data DATA [DATA ...]
                        Source cube file
  -p PROJECTION, --projection PROJECTION
                        Desired map projection
  -m MAP, --map MAP     Input map
```

#### Examples:
Project an input cube to equirectangular, preserving the cube's resolution.
```
project.py -d 1173J2-002_Vg2_CALLISTO_CLEAR_1979-07-08_14.06.23.cub -p equirectangular
```
Project an input cube to match the projection and resolution of another cube.
```
project.py -d 1173J2-002_Vg2_CALLISTO_CLEAR_1979-07-08_14.06.23.cub -m map.cub
```

### matchmap.py
Batch processes input cubes to match the projection and resolution of another map projected input cube.
```
usage: matchmap.py [-h] -d DATA [DATA ...] [-m MAP] -o OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  -d DATA [DATA ...], --data DATA [DATA ...]
                        Source cube file
  -m MAP, --map MAP     Input map
  -o OUTPUT, --output OUTPUT
                        Output Directory
```
#### Examples:
Project a cube to equirectangular, then process all the cubes to match.
```
project.py -d 1173J2-002_Vg2_CALLISTO_CLEAR_1979-07-08_14.06.23.cub -p equirectangular
mv 1173J2-002_Vg2_CALLISTO_CLEAR_1979-07-08_14.06.23_equirectangular.cub map.cub
mkdir remapped
matchmap.py -d *CALLISTO*cub -m map.cub -o remapped
```

### matchcam.py
Convert the camera geometry of an input cube(s) to match a specific master.
```
usage: matchmap.py [-h] -d DATA [DATA ...] [-m MAP] -o OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  -d DATA [DATA ...], --data DATA [DATA ...]
                        Source cube file
  -m MAP, --map MAP     Input map
  -o OUTPUT, --output OUTPUT
                        Output Directory
```

#### Examples:
Process a directory full of cubes to match a single camera geometry.
```
mkdir recammed
matchmap.py -d *cub -m 1173J2-002_Vg2_CALLISTO_CLEAR_1979-07-08_14.06.23.cub -o recammed
```
