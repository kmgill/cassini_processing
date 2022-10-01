#!/bin/bash

unzip -o approach_movie_PJ??-images.zip
unzip -o approach_movie_PJ??-metadata.zip

for image_id in `ls -1 *png | cut -c -25 | sort | uniq | grep C00`; do
    echo Processing $image_id

    process_junocam.py -fFdvlL -o vt=2 projection=jupiterequirectangular -s 0.001 -p -I ${image_id}-raw.png -m ${image_id}.json

    if [ $? -ne 0 ]; then
        echo "Error detected. Exiting batch script."
        exit 1
    fi
done