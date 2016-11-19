
import os
from isis3 import info
from isis3 import galileo
from isis3 import cameras
from isis3 import filters
from isis3 import mathandstats
from isis3 import trimandmask


def output_filename(file_name):
    dirname = os.path.dirname(file_name)
    if len(dirname) > 0:
        dirname += "/"
    product_id = info.get_product_id(file_name)
    target = info.get_target(file_name)
    filter1, filter2 = info.get_filters(file_name)
    image_time = info.get_image_time(file_name)
    out_file = "{dirname}{product_id}_{target}_{filter1}_{image_date}".format(dirname=dirname,
                                                                                        product_id=product_id,
                                                                                        target=target,
                                                                                        filter1=filter1,
                                                                                        image_date=image_time.strftime('%Y-%m-%d_%H.%M.%S'))
    return out_file

def is_supported_file(file_name):
    if file_name[-3:].upper() in ("CUB",):
        value = info.get_field_value(file_name,  "SpacecraftName", grpname="Instrument")
        return value == "Galileo Orbiter"
    elif file_name[-3:].upper() in ("LBL", ):
        value = info.get_field_value(file_name, "SPACECRAFT_NAME")
        return value == "GALILEO ORBITER"
    else:
        return False


def process(from_file_name, is_verbose=False, skip_if_cub_exists=False):
    pass

"""

echo "Importing to cube..."
gllssi2isis from=$f to=tmp/__${id}_raw.cub

#echo "Filling in Gaps..."
#fillgap from=tmp/__${id}_raw.cub to=tmp/__${id}_fill0.cub interp=cubic direction=sample

echo "Initializing Spice..."
spiceinit from=tmp/__${id}_raw.cub

echo "Calibrating cube..."
gllssical from=tmp/__${id}_raw.cub to=tmp/__${id}_cal.cub

echo "Running Noise Filter..."
noisefilter from=tmp/__${id}_cal.cub to=tmp/__${id}_stdz.cub toldef=stddev tolmin=2.5 tolmax=2.5 replace=null samples=5 lines=5

echo "Filling in Nulls..."
lowpass from=tmp/__${id}_stdz.cub to=tmp/__${id}_fill.cub samples=3 lines=3 filter=outside null=yes hrs=no his=no lrs=no replacement=center

echo "Removing Frame-Edge Noise..."
trim from=tmp/__${id}_fill.cub to=$OUT_FILE_CUB top=2 bottom=2 left=2 right=2

echo "Exporting TIFF..."
isis2std from=$OUT_FILE_CUB to=$OUT_FILE_TIFF format=tiff bittype=u16bit maxpercent=99.99

echo "Cleaning up..."
rm tmp/__${id}*.cub
"""