#!/usr/bin/env python

import os
import sys
import spiceypy as spice
import math
import numpy as np
from PIL import Image
from libtiff import TIFFimage
import argparse
import json


from sciimg.isis3 import info
from sciimg.isis3 import scripting
from sciimg.isis3 import importexport


from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *


def get_screen_dimensions(default=(1024,1024)):
    try:
        import Tkinter
        root = Tkinter.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        return (width, height)
    except:
        return default

WINDOW_SIZE = get_screen_dimensions()


PROGRAMS = {}
JUPITER_TEXTURE_ID = None
JUNOCAM_IMAGE_TEXTURE_ID = None
DISTANCE = 1.0
FRAME_NUMBER = 0
FOV = 90

cube_file_red = None
cube_file_green = None
cube_file_blue = None

IMAGE_PROPERTIES = {
    "data": None,
    "image_time": None,
    "interframe_delay": None,
    "min_lat": None,
    "max_lat": None,
    "min_lon": None,
    "max_lon": None,
    "output": None,
    "scale": 1.0
}


def reshape(width, height):
    glViewport(0, 0, width, height);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity()
    aspect = float(width) / float(height)
    gluPerspective(FOV, aspect, 100, 900000.0)
    glutPostRedisplay()


def convert_16bitgrayscale_to_8bitRGB(im):
    im = np.copy(np.asarray(im, dtype=np.float32))

    im = im / 65535.0
    im = im * 255.0
    im = np.asarray(np.dstack((im, im, im)), dtype=np.uint8)
    return im

def load_texture(name, from16bitTiff=False):
    # global texture
    image = Image.open(name)

    ix = image.size[0]
    iy = image.size[1]

    if from16bitTiff:
        im = convert_16bitgrayscale_to_8bitRGB(image)
        im = Image.fromarray(im)
        image = im.tobytes("raw", "RGBX", 0, -1)
    else:
        image = image.tobytes("raw", "RGBX", 0, -1)

    # Create Texture
    id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, id)  # 2d texture (x and y size)

    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    return id

def create_dummy_image(width, height):
    im = np.zeros((width, height, 3), dtype=np.uint8)
    im = Image.fromarray(im)
    image = im.tobytes("raw", "RGBX", 0, -1)
    return image



def render(junocam_texture_id):
    spacecraftOrientation, jupiterState, spacecraftState, jupiterRotation, instrumentCubeOrientation, instrumentOrientation = calculate_orientations(
        frame_number=IMAGE_PROPERTIES["frame_number"])

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity();

    lighting = False

    if lighting is True:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        lightPosition = (-jupiterState[0], -jupiterState[1], -jupiterState[2])
        glLightfv(GL_LIGHT0, GL_POSITION, lightPosition, 0);
        glShadeModel(GL_SMOOTH);
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0), 0)
    else:
        glDisable(GL_LIGHTING)

    glPushMatrix()

    glRotatef(jupiterRotation[0], 1, 0, 0)
    glRotatef(jupiterRotation[1], 0, 1, 0)
    glRotatef(jupiterRotation[2], 0, 0, 1)

    glRotatef(-spacecraftOrientation[0], 1, 0, 0)
    glRotatef(-spacecraftOrientation[1], 0, 1, 0)
    glRotatef(-spacecraftOrientation[2], 0, 0, 1)

    glRotatef(-instrumentCubeOrientation[0], 1, 0, 0)
    glRotatef(-instrumentCubeOrientation[1], 0, 1, 0)
    glRotatef(-instrumentCubeOrientation[2], 0, 0, 1)

    glRotatef(-instrumentOrientation[0], 1, 0, 0)
    glRotatef(-instrumentOrientation[1], 0, 1, 0)
    glRotatef(-instrumentOrientation[2], 0, 0, 1)

    spacecraftState *= IMAGE_PROPERTIES["scale"]
    glTranslatef(-spacecraftState[0], -spacecraftState[1], -spacecraftState[2])

    # draw_image_spherical(JUPITER_TEXTURE_ID, -90, 90, -180, 180)

    draw_image_spherical(junocam_texture_id,
                         IMAGE_PROPERTIES["min_lat"],
                         IMAGE_PROPERTIES["max_lat"],
                         IMAGE_PROPERTIES["min_lon"],
                         IMAGE_PROPERTIES["max_lon"])

    glPopMatrix()


def export_fb():
    pixels = glReadPixels(0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1], GL_RGBA, GL_UNSIGNED_BYTE)

    dt = np.dtype(np.uint8)
    dt = dt.newbyteorder('>')
    pixels = np.frombuffer(pixels, dtype=dt)
    pixels = np.flip(np.reshape(pixels, (-1, WINDOW_SIZE[0], 4)), 0)
    save_image(IMAGE_PROPERTIES["output"], pixels)

    return pixels

def display():
    print "Drawing..."
    global FRAME_NUMBER, DISTANCE

    fbId = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, fbId)
    dummy_image = create_dummy_image(WINDOW_SIZE[0], WINDOW_SIZE[1])
    frameBufferName = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, frameBufferName)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, WINDOW_SIZE[0], WINDOW_SIZE[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, dummy_image)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, frameBufferName, 0)
    glDrawBuffers(1, GL_COLOR_ATTACHMENT0)
    glBindFramebuffer(GL_FRAMEBUFFER, frameBufferName)

    configure_for_projected_cube(cube_file_red)
    junocam_texture_id = load_texture(IMAGE_PROPERTIES["data"], True)
    render(junocam_texture_id)
    red_pixels = export_fb()

    configure_for_projected_cube(cube_file_green)
    junocam_texture_id = load_texture(IMAGE_PROPERTIES["data"], True)
    render(junocam_texture_id)
    green_pixels = export_fb()

    configure_for_projected_cube(cube_file_blue)
    junocam_texture_id = load_texture(IMAGE_PROPERTIES["data"], True)
    render(junocam_texture_id)
    blue_pixels = export_fb()

    rgba_buffer = np.zeros(red_pixels.shape, dtype=np.uint8)

    for y in range(0, red_pixels.shape[0]):
        for x in range(0, red_pixels.shape[1]):
            r = red_pixels[y][x][0]
            g = green_pixels[y][x][0]
            b = blue_pixels[y][x][0]
            rgba_buffer[y][x][0] = r
            rgba_buffer[y][x][1] = g
            rgba_buffer[y][x][2] = b
            rgba_buffer[y][x][3] = 255

    save_image(IMAGE_PROPERTIES["combined_output"], rgba_buffer)

    window_mode = False
    if window_mode is True:
        glFlush()
        glutSwapBuffers()
    else:
        sys.exit(0)

def save_image(path, data):
    im = Image.fromarray(data)
    im.save(path)
    #data_matrix = data.astype(np.uint16) / 255.0 * 65535.0
    #tiff = TIFFimage(data, description='')
    #tiff.write_file(path, compression='none')


def draw_jupiter_sphere():
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, JUPITER_TEXTURE_ID)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FLAT)
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluQuadricOrientation(quadric, GLU_OUTSIDE);
    gluQuadricTexture(quadric, True)
    gluSphere(quadric, 71492., 128, 64)
    gluDeleteQuadric(quadric)


def calc_surface_normal(v0, v1, v2):
    v0 = np.array(v0)
    v1 = np.array(v1)
    v2 = np.array(v2)

    U = v1 - v0
    V = v2 - v1

    N = np.cross(U, V)
    return N


def draw_image_spherical(texture_id, minLat, maxLat, minLon, maxLon, latSlices = 32, lonSlices = 64):
    global PROGRAMS

    if not texture_id in PROGRAMS:
        PROGRAMS[texture_id] = glGenLists(1)
        glNewList(PROGRAMS[texture_id], GL_COMPILE)

        latRes = (maxLat - minLat) / float(latSlices)
        lonRes = (maxLon - minLon) / float(lonSlices)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        for y in range(0, int(latSlices)):
            glBegin(GL_TRIANGLES)
            for x in range(0, int(lonSlices)):
                mx_lat = maxLat - (latRes * y)
                mn_lon = minLon + (lonRes * x)

                mn_lat = mx_lat - latRes
                mx_lon = mn_lon + lonRes

                mx_lat = math.radians(mx_lat)
                mn_lat = math.radians(mn_lat)
                mx_lon = math.radians(mx_lon)
                mn_lon = math.radians(mn_lon)

                ulVector = spice.srfrec(599, mn_lon, mx_lat)
                llVector = spice.srfrec(599, mn_lon, mn_lat)
                urVector = spice.srfrec(599, mx_lon, mx_lat)
                lrVector = spice.srfrec(599, mx_lon, mn_lat)

                ulUV = (x / float(lonSlices), 1.0 - y / float(latSlices))
                llUV = ( x / float(lonSlices), 1.0 - (y + 1) / float(latSlices))
                urUV = ((x + 1) / float(lonSlices), 1.0 - y / float(latSlices))
                lrUV = ((x + 1) / float(lonSlices), 1.0 - (y + 1) / float(latSlices))

                N = calc_surface_normal(ulVector, llVector, urVector)
                glNormal3f(N[0], N[1], N[2])

                glTexCoord2f(ulUV[0], ulUV[1])
                glVertex3f(ulVector[0], ulVector[1], ulVector[2])

                glTexCoord2f(llUV[0], llUV[1])
                glVertex3f(llVector[0], llVector[1], llVector[2])

                glTexCoord2f(urUV[0], urUV[1])
                glVertex3f(urVector[0], urVector[1], urVector[2])

                N = calc_surface_normal(urVector, llVector, lrVector)
                glNormal3f(N[0], N[1], N[2])

                glTexCoord2f(urUV[0], urUV[1])
                glVertex3f(urVector[0], urVector[1], urVector[2])

                glTexCoord2f(llUV[0], llUV[1])
                glVertex3f(llVector[0], llVector[1], llVector[2])

                glTexCoord2f(lrUV[0], lrUV[1])
                glVertex3f(lrVector[0], lrVector[1], lrVector[2])
            glEnd()
        glEndList()
    glCallList(PROGRAMS[texture_id])


def keyboard(c, x, y):
    global IMAGE_PROPERTIES, DISTANCE, FOV
    """keyboard callback."""
    if c in ["q", chr(27)]:
        sys.exit(0)
    elif c == 'f':
        IMAGE_PROPERTIES["frame_number"] += 1.0
        print IMAGE_PROPERTIES["frame_number"]
    elif c == 'F':
        IMAGE_PROPERTIES["frame_number"] += 100.0
        print IMAGE_PROPERTIES["frame_number"]
    elif c == 'b':
        IMAGE_PROPERTIES["frame_number"] -= 1.0
        print IMAGE_PROPERTIES["frame_number"]
    elif c == 'B':
        IMAGE_PROPERTIES["frame_number"] -= 100.0
        print IMAGE_PROPERTIES["frame_number"]
    elif c == 'i':
        IMAGE_PROPERTIES["scale"] -= 0.1
    elif c == 'o':
        IMAGE_PROPERTIES["scale"] += 0.1
    elif c == 'k':
        FOV -= 1.0
    elif c == 'l':
        FOV += 1.0

    if DISTANCE < 1.0:
        DISTANCE = 1.0
    glutPostRedisplay()


def mouse(button, state, x, y):
    pass


def motion(x1, y1):
    pass


def init_glut(argv):
    """glut initialization."""
    glutInit(argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(*WINDOW_SIZE)
    glutCreateWindow(argv[0])
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)

def init_opengl():
    global JUPITER_TEXTURE_ID, JUNOCAM_IMAGE_TEXTURE_ID
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_POLYGON_SMOOTH)
    glShadeModel(GL_SMOOTH)
    JUPITER_TEXTURE_ID = load_texture('/Users/kgill/repos/JunoCamProcessing/jupiter_johnw_texture_8192x4096.png', False)
    glEnable(GL_TEXTURE_2D)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glEnable(GL_NORMALIZE)
    glClearColor(0.0, 0.0, 0.0, 1.0)


def rotation_matrix_to_euler_angles(R):
    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.array([x, y, z])


def radians_xyz_to_degrees_xyz(xyz):
    return np.array([math.degrees(xyz[0]), math.degrees(xyz[1]), math.degrees(xyz[2])])


def calculate_orientations(frame_number=0):
    et = spice.str2et(IMAGE_PROPERTIES["image_time"])
    et = et + (frame_number * IMAGE_PROPERTIES["interframe_delay"])

    jupiterState, lt = spice.spkpos('JUPITER', et, 'IAU_SUN', 'NONE', 'SUN')

    spacecraftState, lt = spice.spkpos('JUNO_SPACECRAFT', et, 'IAU_JUPITER', 'NONE', 'JUPITER')

    m = spice.pxform("J2000", "IAU_JUPITER", et)
    jupiterRotation = radians_xyz_to_degrees_xyz(rotation_matrix_to_euler_angles(m))

    m = spice.pxform("IAU_JUPITER", "JUNO_SPACECRAFT", et)
    spacecraftOrientation = radians_xyz_to_degrees_xyz(rotation_matrix_to_euler_angles(m))

    m = spice.pxform("JUNO_SPACECRAFT", "JUNO_JUNOCAM_CUBE", et)
    instrumentCubeOrientation = radians_xyz_to_degrees_xyz(rotation_matrix_to_euler_angles(m))

    m = spice.pxform("JUNO_JUNOCAM_CUBE", "JUNO_JUNOCAM", et)
    instrumentOrientation = radians_xyz_to_degrees_xyz(rotation_matrix_to_euler_angles(m))

    return spacecraftOrientation, jupiterState, spacecraftState, jupiterRotation, instrumentCubeOrientation, instrumentOrientation


def main(argv=None):
    if argv is None:
        argv = sys.argv
    init_glut(argv)
    init_opengl()
    return glutMainLoop()



def load_kernels(kernelbase):
    kernels = [
        "base/kernels/lsk/naif0012.tls",
        "base/kernels/pck/pck00009.tpc",
        "juno/kernels/fk/juno_v12.tf",
        "juno/kernels/ik/juno_junocam_v02.ti",
        "juno/kernels/lsk/naif0012.tls",
        "juno/kernels/sclk/JNO_SCLKSCET.00065.tsc",
        "juno/kernels/spk/spk_ref_180429_210731_180509.bsp",
        "juno/kernels/spk/spk_ref_160226_180221_160226.bsp",
        "juno/kernels/spk/spk_ref_160829_190912_161027.bsp",
        "juno/kernels/spk/spk_ref_161212_210731_170320.bsp",
        "juno/kernels/spk/de438s.bsp",
        "juno/kernels/spk/jup310.bsp",
        "juno/kernels/spk/juno_struct_v03.bsp"
    ]

    for file in os.listdir("%s/juno/kernels/ck"%kernelbase):
        if file[-3:] == ".bc":
            kernels.append("JUNO/kernels/ck/%s" % file)

    #for file in os.listdir("/Users/kgill/ISIS/data/juno/kernels/spk"):
    #    if file[-4:] == ".bsp":
    #        kernels.append("juno/kernels/spk/%s" % file)

    for kernel in kernels:
        spice.furnsh("%s/%s" % (kernelbase, kernel))



def cube_to_tiff(cube_file):

    source_dirname = os.path.dirname(cube_file)
    if source_dirname == "":
        source_dirname = "."

    work_dir = "%s/work" % source_dirname
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)

    bn = os.path.basename(cube_file)

    output_file = "%s/%s.tif"%(work_dir, bn[:-4])
    importexport.isis2std_grayscale(to_tiff=output_file, from_cube=cube_file)
    return output_file


def configure_for_projected_cube(cube_file=None, label_file=None, combined_output=None, frame_offset=None, verbose=False):
    global IMAGE_PROPERTIES

    if cube_file is None:
        cube_file = IMAGE_PROPERTIES["cube_file"]
    if label_file is None:
        label_file = IMAGE_PROPERTIES["label_file"]
    if combined_output is None:
        combined_output = IMAGE_PROPERTIES["combined_output"]
    if frame_offset is None:
        frame_offset = IMAGE_PROPERTIES["frame_offset"]
    output = "%s_rendered.tif"%cube_file[:-4]


    image_time = info.get_field_value(label_file, "IMAGE_TIME")
    interframe_delay = info.get_field_value(label_file, "INTERFRAME_DELAY")

    num_lines = info.get_field_value(label_file, "LINES")

    frame_number = int(round(float(num_lines) / 128.0 / 3.0 / 2.0)) + frame_offset

    min_lat = scripting.getkey(cube_file, "MinimumLatitude", grpname="Mapping")
    max_lat = scripting.getkey(cube_file, "MaximumLatitude", grpname="Mapping")
    min_lon = scripting.getkey(cube_file, "MinimumLongitude", grpname="Mapping")
    max_lon = scripting.getkey(cube_file, "MaximumLongitude", grpname="Mapping")

    tiff_file = cube_to_tiff(cube_file)

    IMAGE_PROPERTIES = {
        "cube_file": cube_file,
        "label_file": label_file,
        "data": tiff_file,
        "image_time": image_time,
        "interframe_delay": float(interframe_delay),
        "min_lat": float(min_lat),
        "max_lat": float(max_lat),
        "min_lon": float(min_lon),
        "max_lon": float(max_lon),
        "output": output,
        "frame_number": frame_number,
        "frame_offset": frame_offset,
        "scale": 1.0,
        "combined_output": combined_output
    }

    if verbose is True:
        print json.dumps(IMAGE_PROPERTIES, indent=4)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--red", help="Input Projected JunoCam Image for red (cube formatted)", required=True, type=str)
    parser.add_argument("-g", "--green", help="Input Projected JunoCam Image for green (cube formatted)", required=True,
                        type=str)
    parser.add_argument("-b", "--blue", help="Input Projected JunoCam Image for blue (cube formatted)", required=True,
                        type=str)
    parser.add_argument("-l", "--label", help="Input JunoCam Label File (PVL formatted)", required=True, type=str)
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-k", "--kernelbase", help="Base directory for spice kernels", required=False, type=str, default="/Users/kgill/ISIS/data")
    parser.add_argument("-o", "--output", help="Output file path", required=True, type=str, default=None)
    parser.add_argument("-f", "--frameoffset", help="Frame offset", required=False, type=int, default=0)
    parser.add_argument("-F", "--fov", help="Field of view (degrees)", required=False, type=int, default=90)
    args = parser.parse_args()

    lbl_file = args.label
    cube_file_red = args.red
    cube_file_green = args.green
    cube_file_blue = args.blue
    verbose = args.verbose
    kernelbase = args.kernelbase
    output = args.output
    frame_offset = args.frameoffset


    FOV = args.fov

    configure_for_projected_cube(cube_file_red, lbl_file, output, frame_offset, verbose)

    load_kernels(kernelbase)

    #FRAME_NUMBER = 13
    sys.exit(main())