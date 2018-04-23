# Processing JunoCam Images

This guide assumes you have a working installation of this software. Additionally, you will need to have the latest version of 
[ISIS3](https://isis.astrogeology.usgs.gov/index.html) and the latest [Juno spice kernels](http://naif.jpl.nasa.gov/pub/naif/JUNO/). 
You'll need to modify the 'makedb' script in the 'spk' directory to include the predicted trajectory kernels.

## Preparing Raw JunoCam Data

Raw JunoCam images are posted to the [mission website](https://www.missionjuno.swri.edu/junocam/processing) a couple days after Perijove.
These are provided as PNG images with metadata in a JSON file. 

The raw data needs to be in a format that can be ingested by ISIS3 while preserving all the metadata. I do that by converting it into a format more-or-less matching PDS archive VICAR files. To do this, you can use junocam_png_to_img.py:

```
junocam_png_to_img.py -p input_junocam_file.png -m input_metadata_file.json
```

This will create an .img file with the image, and a .lbl file as a seperate metadata label. 


## Processing JunoCam Images

Process a PDS formatted JunoCam image using process.py:

```
process.py -d input_junocam_file.lbl
```

This will perform the following steps:
1. Convert JunoCam images to ISIS Cube files ([junocam2isis](https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/junocam2isis/junocam2isis.html))
2. Optionally trims top and bottom of framelets by a few pixels. ([trim](https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/trim/trim.html))

   This is primarily useful when processing from raw data which tends to result in lines on the top an bottom of the framelets. 
   Specifying the option, for example, `-o vt=4` will trim each framelets by 4 pixels off the top and bottom.

3. Initialize spice kernels on each framelet ([spiceinit](https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/spiceinit/spiceinit.html))
4. Map projects framelets to equirectangular ([cam2map](https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/cam2map/cam2map.html))

   Specify another projection by using, for example, `-o projection=mercator`. Projection must have a corresponding map file in the ISIS system.

5. Assembles framelets into mosaics ([automos](https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/automos/automos.html))
6. Optionally runs a histogram equalization on the mosaics ([histeq](https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/histeq/histeq.html))

   To run this, specify `-o histeq=true`.
   
7. Exports the map projected mosaics to tiff files (unsigned 16 bit). ([isis2std](https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/isis2std/isis2std.html))
8. Reprojects the mosaics to match the camera perspective mid-observation ([map2cam](https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/map2cam/map2cam.html))
9. Optionally runs a histogram equalization on the camera-projected mosaics ([histeq](https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/histeq/histeq.html))

   To run this, specify `-o histeq=true`.
   
7. Exports the camera-projected mosaics to tiff files (unsigned 16 bit), both as individual grayscale images and as a combined RGB image. ([isis2std](https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/isis2std/isis2std.html))
10. Cleans up. Using `-n` option will skip this step and leave all the intermediate cube files in the `work` directory.


At this point you are left with three grayscale map-projected images, three grayscale camera-projected imagees, and one color camera-projected image. It is now up to you to decide which of the output images to use and how to finalize them. I've been using the grayscale camera-projected images, bringing them into Photoshop for fine-tuned alignment, then Lightroom for color and contrast adjustments.
