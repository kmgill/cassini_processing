#!/bin/bash

red_cube=`ls JNC*RED*Mosaic.cub`
green_cube=`ls JNC*GREEN*Mosaic.cub`
blue_cube=`ls JNC*BLUE*Mosaic.cub`
lbl_file=`ls JNC*lbl`
outfile=`ls JNC*RED*Mosaic.cub | awk '{print substr($1, 0, 25);}'`_Rendered_RGB.tif

echo Red Cube: $red_cube
echo Green Cube: $green_cube
echo Blue Cube: $blue_cube
echo Label File: $lbl_file
echo Output: $outfile


render_junocam_cube.py -r $red_cube -g $green_cube -b $blue_cube -l $lbl_file -o $outfile $@