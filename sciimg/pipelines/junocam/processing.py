import os
import sys
import glob
from sciimg.isis3 import info
from sciimg.isis3 import juno
from sciimg.isis3 import cameras
from sciimg.isis3 import mathandstats
from sciimg.isis3 import trimandmask
from sciimg.isis3 import importexport
from sciimg.isis3 import mosaicking
from sciimg.isis3._core import printProgress
from sciimg.isis3 import utility
from sciimg.isis3 import scripting
from sciimg.isis3 import mapprojection
import multiprocessing
import numpy as np
import traceback

def print_r(*args):
    s = ' '.join(map(str, args))
    print(s)


def output_filename(file_name):
    dirname = os.path.dirname(file_name)
    if len(dirname) > 0:
        dirname += "/"


def is_supported_file(file_name):
    if file_name is None:
        return False

    if file_name[-3:].upper() in ("CUB",):
        value = info.get_field_value(file_name,  "SpacecraftName", grpname="Instrument")
        return value is not None and value.decode('UTF-8') == "JUNO"
    elif file_name[-3:].upper() in ("LBL", ):
        value = info.get_field_value(file_name, "SPACECRAFT_NAME")
        return value is not None and value.decode('UTF-8') == "JUNO"
    else:
        return False


def assemble_mosaic(color, source_dirname, product_id, min_lat, max_lat, min_lon, max_lon, is_verbose=False):
    mapped_dir = "%s/work/mapped" % source_dirname
    list_file = "%s/work/mapped/cubs_%s.lis" % (source_dirname, product_id)
    cub_files = glob.glob('%s/__%s_raw_%s_*.cub' % (mapped_dir, product_id, color.upper()))

    f = open(list_file, "w")
    for cub_file in cub_files:
        f.write(cub_file)
        f.write("\n")
    f.close()

    mosaic_out = "%s/%s_%s_Mosaic.cub" % (source_dirname, product_id, color.upper())
    s = mosaicking.automos(list_file,
                           mosaic_out,
                           priority=mosaicking.Priority.AVERAGE,
                           grange=mosaicking.Grange.USER,
                           minlat=min_lat,
                           maxlat=max_lat,
                           minlon=min_lon,
                           maxlon=max_lon)
    if is_verbose:
        print(s)

    return mosaic_out


def export(out_file_cub, is_verbose=False):
    out_file_tiff = "%s.tif"%out_file_cub[:-4]
    s = importexport.isis2std_grayscale("%s" % (out_file_cub),
                                        "%s" % (out_file_tiff))
    if is_verbose:
        print(s)


def clean_dir(dir, product_id):
    files = glob.glob('%s/*%s*' % (dir, product_id))
    for file in files:
        os.unlink(file)


def trim_vertical(cub_file, trim_pixels=2):
    trim_file = "%s_trim.cub"%cub_file[:-4]
    trimandmask.trim(cub_file, trim_file, top=trim_pixels, bottom=trim_pixels, left=0, right=0)
    os.unlink(cub_file)
    os.rename(trim_file, cub_file)

def trim_cube(args):
    cub_file = args["cub_file"]
    trim_pixels = args["trim_pixels"]
    trim_vertical(cub_file, trim_pixels)

def trim_cubes(work_dir, product_id, trim_pixels=2, num_threads=multiprocessing.cpu_count()):
    cub_files = glob.glob('%s/__%s_raw_*.cub' % (work_dir, product_id))

    params = [{"cub_file":cub_file, "trim_pixels": trim_pixels} for cub_file in cub_files]
    p = multiprocessing.Pool(num_threads)
    xs = p.map(trim_cube, params)


def histeq_cube(cub_file, work_dir, product_id):
    hist_file = "%s/__%s_hist.cub" % (work_dir, product_id)
    mathandstats.histeq("%s+1"%cub_file, hist_file, minper=0.0, maxper=100.0)
    os.unlink(cub_file)
    os.rename(hist_file, cub_file)



def initspice_for_cube(args):
    cub_file = args["cub_file"]
    if "verbose" in args:
        verbose = args["verbose"]
    else:
        verbose = False

    if verbose is True:
        print_r("Initializing spice on cube file:", cub_file)

    s = cameras.spiceinit(cub_file)

    if verbose is True:
        print_r(s)

    return s




def get_coord_range_from_cube(cub_file):
    min_lat = float(scripting.getkey(cub_file, "MinimumLatitude", grpname="Mapping"))
    max_lat = float(scripting.getkey(cub_file, "MaximumLatitude", grpname="Mapping"))
    min_lon = float(scripting.getkey(cub_file, "MinimumLongitude", grpname="Mapping"))
    max_lon = float(scripting.getkey(cub_file, "MaximumLongitude", grpname="Mapping"))
    return (min_lat, max_lat, min_lon, max_lon)

def map_project_cube(args):
    cub_file = args["cub_file"]
    out_file = args["out_file"]
    map_file = args["map"]
    if "verbose" in args:
        verbose = args["verbose"]
    else:
        verbose = False

    if verbose is True:
        print_r("Map projecting cube file", cub_file)

    try:
        s = cameras.cam2map(cub_file, out_file, map=map_file, resolution="MAP")
        if verbose is True:
            print_r(s)
        return get_coord_range_from_cube(out_file)
    except:
        return None #Just eat the exception for now.


"""
    JunoCam additional options:
    projection=<projection>
    vt=<number>
    histeq=true|false
"""
def process_pds_data_file(from_file_name, is_verbose=False, skip_if_cub_exists=False, init_spice=True, nocleanup=False, additional_options={}, num_threads=multiprocessing.cpu_count()):
    #out_file = output_filename(from_file_name)
    #out_file_tiff = "%s.tif" % out_file
    #out_file_cub = "%s.cub" % out_file

    num_steps = 17

    if "projection" in additional_options:
        projection = additional_options["projection"]
    else:
        projection = "jupiterequirectangular"

    if "st" in additional_options: # st means "Skip Triplets.
        skip_triplets = int(additional_options["st"])
        if is_verbose:
            print("Skipping first and last", skip_triplets, "triplets")
    else:
        skip_triplets = None

    source_dirname = os.path.dirname(from_file_name)
    if source_dirname == "":
        source_dirname = "."

    work_dir = "%s/work" % source_dirname
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)




    product_id = info.get_product_id(from_file_name)
    sub_spacecraft_longitude = info.get_property(from_file_name, "SUB_SPACECRAFT_LONGITUDE")
    print("Product Id:", product_id)
    print("Sub Spacecraft Longitude:", sub_spacecraft_longitude)


    mapped_dir = "%s/work/mapped" % source_dirname
    if not os.path.exists(mapped_dir):
        os.mkdir(mapped_dir)


    if is_verbose:
        print("Importing to cube...")
    else:
        printProgress(0, num_steps, prefix="%s: "%from_file_name)

    s = juno.junocam2isis(from_file_name, "%s/__%s_raw.cub"%(work_dir, product_id))
    if is_verbose:
        print(s)


    if "vt" in additional_options:
        trim_pixels = int(additional_options["vt"])
        if is_verbose:
            print("Trimming Framelets...")
            print("Vertical trimming: %d pixels"%trim_pixels)
        else:
            printProgress(1, num_steps, prefix="%s: "%from_file_name)

        trim_cubes(work_dir, product_id, trim_pixels=trim_pixels, num_threads=num_threads)


    if init_spice is True:
        if is_verbose:
            print("Initializing Spice...")
        else:
            printProgress(2, num_steps, prefix="%s: "%from_file_name)
        cub_files = glob.glob('%s/__%s_raw_*.cub'%(work_dir, product_id))

        init_spice_params = [{"cub_file": cub_file, "verbose": is_verbose} for cub_file in cub_files]
        p = multiprocessing.Pool(num_threads)
        xs = p.map(initspice_for_cube, init_spice_params)
    

    mid_num = int(round(len(glob.glob('%s/__%s_raw_*.cub' % (work_dir, product_id))) / 3.0 / 2.0))

    mid_file = "%s/__%s_raw_GREEN_%04d.cub"%(work_dir, product_id, mid_num)
    map_file = "%s/__%s_map.cub"%(work_dir, product_id)


    if is_verbose:
        print("Starting Map...")
    else:
        printProgress(3, num_steps, prefix="%s: " % from_file_name)

    s = cameras.cam2map(mid_file, map_file, projection=projection)
    if is_verbose:
        print(s)

    if is_verbose:
        print("Map Projecting Stripes...")
    else:
        printProgress(4, num_steps, prefix="%s: " % from_file_name)

    cub_files_blue = glob.glob('%s/__%s_raw_BLUE_*.cub' % (work_dir, product_id))
    cub_files_green = glob.glob('%s/__%s_raw_GREEN_*.cub' % (work_dir, product_id))
    cub_files_red = glob.glob('%s/__%s_raw_RED_*.cub' % (work_dir, product_id))

    if skip_triplets is not None:
        cub_files_blue.sort()
        cub_files_blue = cub_files_blue[skip_triplets:-skip_triplets]
        cub_files_green.sort()
        cub_files_green = cub_files_green[skip_triplets:-skip_triplets]
        cub_files_red.sort()
        cub_files_red = cub_files_red[skip_triplets:-skip_triplets]
    cub_files = cub_files_blue + cub_files_green + cub_files_red


    params = [{"cub_file": cub_file, "out_file": "%s/%s"%(mapped_dir, os.path.basename(cub_file)), "map": map_file, "verbose": is_verbose} for cub_file in cub_files]
    p = multiprocessing.Pool(num_threads)
    xs = p.map(map_project_cube, params)

    min_lat = np.min([l[0] for l in xs if l is not None])
    max_lat = np.max([l[1] for l in xs if l is not None])
    min_lon = np.min([l[2] for l in xs if l is not None])
    max_lon = np.max([l[3] for l in xs if l is not None])

    #cub_files = glob.glob('%s/mapped/__%s_raw_*.cub' % (work_dir, product_id))
    #xs = []
    #for cub_file in cub_files:
    #    coord_range = get_coord_range_from_cube(cub_file) #(min_lat, max_lat, min_lon, max_lon)
    #    print(coord_range)
    #    xs.append(coord_range)
    #xs = [[9.7318540896932, 31.467066832209, -14.245802963692, 1.6421180628122], [30.196681748411, 38.994025920211, 323.45564911076, 356.92978658588], [32.593347108127, 39.732759409359, 322.65481226755, 356.72865460936], [10.742129197933, 32.012807114029, -16.681496095326, 1.0806607717237], [28.067378890869, 38.317951823567, 324.57649262312, 357.14019477064], [25.98488878048, 37.691342029567, 325.63359892738, 357.36114080931], [35.115209665722, 40.551730240846, 322.0194753597, 356.53551603001], [47.017389951527, 59.962398524825, 327.96595101583, 355.37818928367], [49.672935270862, 63.342583308867, 333.83352433721, 355.05279734032], [37.896421820332, 41.515733457104, 321.40108363631, 356.34891844266], [42.39516373941, 48.298102728575, 321.60319424782, 355.9868878747], [13.25605652599, 18.960384938856, 13.863915293677, 17.857181939807], [40.960204119179, 44.695225278323, 321.59618265178, 356.16698345022], [54.127769905622, 64.630313387331, 343.16621167771, 354.36360728901], [35.962285389022, 40.803442194315, 321.63959741702, 356.40188851515], [47.735830401532, 61.054060941839, 329.46695994983, 355.10504414524], [31.594831400822, 39.465409680959, 322.99563436763, 356.79415709607], [44.529713181016, 54.937821128049, 324.0426149637, 355.65693946505], [46.258689305337, 58.905353412082, 326.45469012031, 355.43705277398], [34.165624557003, 40.25063200219, 322.21108235054, 356.59638686698], [45.644060915901, 57.649127126387, 325.36885068578, 355.3897850728], [33.245491387852, 39.960993942482, 322.20001994961, 356.60073158969], [42.748053191952, 49.55922798517, 321.83476449395, 355.82081485615], [28.545675282764, 38.513485970032, 324.09992952218, 357.01932227412], [52.122947351847, 64.403606721209, 339.20101522839, 354.64777830083], [39.853973267612, 43.482940164746, 321.36411617752, 356.21954197115], [36.871635233941, 41.129899928184, 321.60443834212, 356.40544051114], [48.5774851906, 62.476686975955, 331.38531902758, 355.14970858727], [30.716472477588, 39.203998350846, 323.27690274078, 356.80602084295], [44.044169660266, 53.581349475091, 322.80113909871, 355.61710818818], [27.257041250984, 38.097529725743, 324.71216747561, 357.21577251301], [56.564357356978, 64.521911819592, 345.90800051556, 353.46000695251], [9.0832728968994, 30.684955702133, -10.871941785648, 2.5501591740565], [22.825562189427, 36.71490738567, 327.60243972029, 357.72185231097], [21.652842193919, 36.176864886619, 329.02098204578, 357.98215155701], [9.5799360767569, 31.27947969605, -13.414356636351, 1.8790102221502], [50.766061868681, 63.982453713738, 335.96386974904, 354.65991765817], [29.369156457657, 38.752921494207, 323.64165977533, 357.00018149919], [8.4099209953744, 29.767337479116, -6.9700290207687, 3.6089382939161], [25.229118051018, 37.487336118552, 326.16535396412, 357.44225047838], [24.525799712371, 37.278699466716, 326.22987896381, 357.47573594031], [26.614139816208, 37.875343097899, 325.37593305475, 357.24207646794], [61.666196747657, 64.303534376607, 350.44601754494, 352.13319986404], [23.466833301755, 36.912984237001, 327.1298477073, 357.68103199163], [8.755146774165, 30.44160882378, -9.9215502752, 2.7847111471653], [8.2323781943248, 28.134835917004, -0.53843341873699, 5.7951710654326], [10.825556955218, 32.168933372423, -17.273190443004, 0.91262472735857], [8.2299320339788, 28.500464806032, -1.734473403548, 5.3514447126302], [18.8275692869, 35.154675759623, 332.13232378194, 358.55352734279], [11.403720750746, 32.36530875179, -18.030049039073, 0.76635791631423], [10.430784601658, 31.836129864006, -15.813008873084, 1.28989750382], [20.895714338452, 35.658551368171, 330.53321238343, 358.25860849449], [8.4351009525818, 27.530374818149, 1.6787569133416, 6.7480041116275], [11.927161567154, 32.686848180832, -19.347565728078, 0.42344338297052], [8.2262620805654, 29.010454000734, -3.95547502325, 4.5903450537321], [20.297146163653, 35.84268201995, 329.83543572485, 358.202085425], [10.217264617675, 31.62849688917, -14.983447703775, 1.4593203155256], [8.6110223991259, 27.079792344555, 2.8343557014731, 7.5040199725087], [12.394498372052, 32.87508204916, -20.025587100734, 0.29628227647857], [8.2313063582399, 29.32035992991, -5.0104875807318, 4.2422658431755], [8.4102741885805, 30.038546116724, -8.0809067160538, 3.3265041815979], [13.577890719102, 33.371994876006, 337.93017369085, 359.87050213203], [9.4948801754236, 25.730403833544, 6.0473829714539, 11.681121043369], [9.4211358109338, 31.056623114945, -12.459032562917, 2.0771140966413], [21.770490452645, 36.366886143439, 328.54611597777, 357.93370292832], [18.679200526846, 35.334863408744, 331.60376910916, 358.48830881516], [9.1178522611093, 26.323188330877, 4.9210525846113, 10.352463624091], [13.050512701782, 33.189361374463, 338.61174313381, 359.98158540403], [43.150541545364, 50.921013026515, 321.87894051854, 355.85118957751], [42.00224253759, 47.111494554622, 321.45931016578, 356.03616621781], [14.190344814603, 33.682410169297, 337.00082205169, 359.57922069488], [10.277573750346, 24.696291523719, 7.9850870359114, 14.714503436966], [17.253164561156, 34.838482798919, 333.04657847631, 358.79489483628], [41.657246332718, 45.760986011873, 321.55955573899, 356.01525954606], [14.596681180919, 33.861618171697, 336.27075429078, 359.48190373569], [10.712340943288, 23.821079708243, 9.1142313052301, 16.245101027051], [16.674053767615, 34.660413157762, 333.63541908703, 358.86963582475], [15.407832366493, 34.17117894949, 335.19366808512, 359.21020606296], [12.803071578174, 20.385199613872, 12.601228560024, 17.974428149874], [16.030407820092, 34.348907099925, 334.5522168277, 359.1248704042], [38.814507857126, 42.314532973367, 321.56795484817, 356.20759798234], [11.806864409344, 22.128876298738, 10.967986900375, 17.970594906504], [45.109228379902, 56.365064439414, 324.63272839964, 355.60811267407], [20.988644620698, 36.015427575378, 329.35613238927, 358.10141097579], [8.393273732171, 27.887488658469, 0.5024202266735, 6.1572159401063], [8.7173348489009, 26.782139842895, 3.7957260521126, 8.7469309257013], [19.176514144726, 35.501689767016, 331.49210370414, 358.3797212464], [43.618814753973, 52.29668192114, 322.51867264496, 355.80377610361], [11.263546344071, 23.239145889508, 9.7489472819831, 17.278925803248], [16.437353204312, 34.509287173794, 333.93999725747, 358.9973412186], [17.83807631878, 35.001220691247, 332.3260993314, 358.67743065896], [9.7170064077932, 25.343722405575, 6.8784034077262, 12.846890737743], [8.331625731489, 29.57294925784, -6.1182787676966, 3.8654962891859], [12.679069864781, 33.038890498123, -21.031033556435, 0.12818477348772], [11.565758365001, 32.534267412694, -18.583509240606, 0.57962385451023], [8.1979029211918, 28.794791065703, -2.9219744477836, 4.8898500782497], [13.798194952182, 33.532814398519, 337.34290841921, 359.7180757434], [8.651166975076, 30.262057176368, -9.0564532449025, 3.0099197600655], [22.294456493046, 36.547581589931, 328.22330069118, 357.84015307345], [24.199376470219, 37.103955867271, 326.75203665948, 357.59396392184], [9.0672914208889, 30.887641943604, -11.830787344829, 2.2784982539678], [15.142013396309, 34.02134185231, 335.63740328544, 359.34284106754]]
    #for x in xs:
    #    if x[2] < 0.0:
    #        x[2] += 360.0
    #        x[3] += 360.0


    #min_lon = np.min([l[2] for l in xs if l is not None])
    #max_lon = np.max([l[3] for l in xs if l is not None])
    #print(min_lon, max_lon)
    #sys.exit(1)



    if is_verbose:
        print("Assembling Red Mosaic...")
    else:
        printProgress(5, num_steps, prefix="%s: " % from_file_name)

    out_file_red = assemble_mosaic("RED", source_dirname, product_id, min_lat, max_lat, min_lon, max_lon, is_verbose)

    if is_verbose:
        print("Assembling Green Mosaic...")
    else:
        printProgress(6, num_steps, prefix="%s: " % from_file_name)

    out_file_green = assemble_mosaic("GREEN", source_dirname, product_id, min_lat, max_lat, min_lon, max_lon, is_verbose)

    if is_verbose:
        print("Assembling Blue Mosaic...")
    else:
        printProgress(7, num_steps, prefix="%s: " % from_file_name)

    out_file_blue = assemble_mosaic("BLUE", source_dirname, product_id, min_lat, max_lat, min_lon, max_lon, is_verbose)






    if "histeq" in additional_options and additional_options["histeq"].upper() in ("TRUE", "YES"):
        if is_verbose:
            print("Running histogram equalization on map projected cubes...")
        else:
            printProgress(8, num_steps, prefix="%s: " % from_file_name)
        histeq_cube(out_file_red, work_dir, product_id)
        histeq_cube(out_file_green, work_dir, product_id)
        histeq_cube(out_file_blue, work_dir, product_id)

    if is_verbose:
        print("Exporting Map Projected Tiffs...")
    else:
        printProgress(9, num_steps, prefix="%s: " % from_file_name)

    export(out_file_red, is_verbose)
    export(out_file_green, is_verbose)
    export(out_file_blue, is_verbose)



    if is_verbose:
        print("Exporting Color Map Projected Cube...")
    else:
        printProgress(10, num_steps, prefix="%s: " % from_file_name)

    out_file_map_rgb_cube_inputs = "%s/%s_Mosaic_RGB.txt" % (source_dirname, product_id)
    out_file_map_rgb_cube = "%s/%s_Mosaic_RGB.cub" % (source_dirname, product_id)

    f = open(out_file_map_rgb_cube_inputs, "w")
    f.write("%s\n"%out_file_red)
    f.write("%s\n" % out_file_green)
    f.write("%s\n" % out_file_blue)
    f.close()

    s = utility.cubeit(out_file_map_rgb_cube_inputs, out_file_map_rgb_cube)
    if is_verbose:
        print(s)

    out_file_map_rgb_tiff = "%s/%s_Mosaic_RGB.tif" % (source_dirname, product_id)
    s = importexport.isis2std_rgb(from_cube_red=out_file_red, from_cube_green=out_file_green, from_cube_blue=out_file_blue, to_tiff=out_file_map_rgb_tiff)
    if is_verbose:
        print(s)

    if is_verbose:
        print("Exporting Color Map Projected Tiff...")
    else:
        printProgress(11, num_steps, prefix="%s: " % from_file_name)

    out_file_map_rgb_tiff = "%s/%s_Mosaic_RGB.tif" % (source_dirname, product_id)
    s = importexport.isis2std_rgb(from_cube_red=out_file_red, from_cube_green=out_file_green, from_cube_blue=out_file_blue, to_tiff=out_file_map_rgb_tiff)
    if is_verbose:
        print(s)


    # Disabling camera reprojection. No longer really need it.
    """
    if is_verbose:
        print("Camera Projecting Mosaics...")
    else:
        printProgress(12, num_steps, prefix="%s: " % from_file_name)

    pad_file = "%s/__%s_raw_GREEN_00%d_padded.cub"%(work_dir, product_id, mid_num)

    utility.pad(mid_file, pad_file, top=2300, right=0, bottom=2300, left=0)

    out_file_red_cam = "%s/%s_%s_Recammed.cub" % (source_dirname, product_id, "RED")
    cameras.map2cam(out_file_red, out_file_red_cam, pad_file)

    out_file_green_cam = "%s/%s_%s_Recammed.cub" % (source_dirname, product_id, "GREEN")
    cameras.map2cam(out_file_green, out_file_green_cam, pad_file)

    out_file_blue_cam = "%s/%s_%s_Recammed.cub" % (source_dirname, product_id, "BLUE")
    cameras.map2cam(out_file_blue, out_file_blue_cam, pad_file)


    if "histeq" in additional_options and additional_options["histeq"].upper() in ("TRUE", "YES"):
        if is_verbose:
            print("Running histogram equalization on camera projected cubes...")
        else:
            printProgress(13, num_steps, prefix="%s: " % from_file_name)
        histeq_cube(out_file_red_cam, work_dir, product_id)
        histeq_cube(out_file_green_cam, work_dir, product_id)
        histeq_cube(out_file_blue_cam, work_dir, product_id)


    if is_verbose:
        print("Exporting Camera Projected Tiffs...")
    else:
        printProgress(14, num_steps, prefix="%s: " % from_file_name)

    export(out_file_red_cam, is_verbose)
    export(out_file_green_cam, is_verbose)
    export(out_file_blue_cam, is_verbose)


    if is_verbose:
        print("Exporting Color Camera Projected Tiff...")
    else:
        printProgress(15, num_steps, prefix="%s: " % from_file_name)

    out_file_cam_rgb_tiff = "%s/%s_RGB.tif" % (source_dirname, product_id)
    s = importexport.isis2std_rgb(from_cube_red=out_file_red_cam, from_cube_green=out_file_green_cam, from_cube_blue=out_file_blue_cam, to_tiff=out_file_cam_rgb_tiff)
    if is_verbose:
        print(s)
    """

    if nocleanup is False:
        if is_verbose:
            print("Cleaning up...")
        else:
            printProgress(16, num_steps, prefix="%s: " % from_file_name)

        clean_dir(work_dir, product_id)
        clean_dir(mapped_dir, product_id)

        dirname = os.path.dirname(out_file_red)
        if len(dirname) > 0:
            dirname += "/"
        if os.path.exists("%sprint.prt"%dirname):
            os.unlink("%sprint.prt"%dirname)
    else:
        if is_verbose:
            print("Skipping clean up...")
        else:
            printProgress(16, num_steps, prefix="%s: " % from_file_name)

    if not is_verbose:
        printProgress(17, num_steps, prefix="%s: "%from_file_name)

    return out_file_map_rgb_tiff