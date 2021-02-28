#!/bin/bash
# Simple method to convert a PDS formatted Voyager ISS image to ISIS3 cube.
# Unlike when sourcing from raw .imq Voyager files and voy2isis, this uses
# pds2isis and does not yet preserve instrument and image metadata in the
# label file. This will (for now) prevent using reprojection/map conversions
# which makes mosaicking a bit more challenging but allows for using calibrated
# and geometrically corrected inputs (GEOMED).


label=$1

echo Converting $label to ISIS cube...

FILTER=`getkey from=$label keyword=FILTER_NAME`
PRODUCT_ID=`getkey from=$label keyword=PRODUCT_ID`
PRODUCT_ID="${PRODUCT_ID%.*}"
CUB_NAME=${PRODUCT_ID}_${FILTER}.cub

echo "  "Filter: $FILTER
echo "  "Product ID: $PRODUCT_ID
echo "  "Cube File Name: $CUB_NAME

echo "  "Converting...
pds2isis from=$label to=$CUB_NAME
echo "  "done
