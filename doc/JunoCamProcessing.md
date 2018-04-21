# Processing JunoCam Images

This guide assumes you have a working installation of this software. Additionally, you will need to have the latest version of 
[ISIS3](https://isis.astrogeology.usgs.gov/index.html) and the latest [Juno spice kernels](http://naif.jpl.nasa.gov/pub/naif/JUNO/). 
You'll need to modify the 'makedb' script in the 'spk' directory to include the predicted trajectory kernels.

## Preparing Raw JunoCam Data

Raw JunoCam images are posted to the [mission website](https://www.missionjuno.swri.edu/junocam/processing) a couple days after Perijove.
These are provided as PNG images with metadata in a JSON file. 
