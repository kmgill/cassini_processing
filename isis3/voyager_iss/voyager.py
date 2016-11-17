

from isis3 import voyager
from isis3 import cameras
from isis3 import filters
from isis3 import mathandstats
from isis3 import trimandmask



def process(from_file_name, is_verbose=False, skip_if_cub_exists=False):
    pass

"""

cho "Importing to cube..."
voy2isis from=$f to=tmp/__${id}_raw.cub

echo "Initializing Spice..."
spiceinit from=tmp/__${id}_raw.cub



echo "Calibrating cube..."
voycal from=tmp/__${id}_raw.cub to=tmp/__${id}_cal.cub

echo "Removing Reseaus..."
findrx from=tmp/__${id}_cal.cub
remrx from=tmp/__${id}_cal.cub to=tmp/__${id}_remrx.cub action=null resvalid=false SDIM=9 LDIM=9

echo "Filling in Gaps..."
#findrx from=__${id}_raw.cub
fillgap from=tmp/__${id}_remrx.cub to=tmp/__${id}_fill0.cub interp=cubic direction=sample
#lowpass from=__${id}_remrx.cub to=__${id}_fill0.cub samples=3 lines=3 filter=outside null=yes hrs=no his=no lrs=no replacement=center


echo "Running Noise Filter..."
noisefilter from=tmp/__${id}_fill0.cub to=tmp/__${id}_stdz.cub toldef=stddev tolmin=2.5 tolmax=2.5 replace=null samples=5 lines=5

echo "Filling in Nulls..."
lowpass from=tmp/__${id}_stdz.cub to=tmp/__${id}_fill.cub samples=3 lines=3 filter=outside null=yes hrs=no his=no lrs=no replacement=center

echo "Removing Frame-Edge Noise..."
trim from=tmp/__${id}_fill.cub to=$OUT_FILE_CUB top=2 bottom=2 left=2 right=2

echo "Exporting TIFF..."
isis2std from=$OUT_FILE_CUB to=$OUT_FILE_TIFF format=tiff bittype=u16bit maxpercent=99.99

echo "Cleaning up..."
rm tmp/__${id}*.cub
rm tmp/__${id}*.pvl
"""