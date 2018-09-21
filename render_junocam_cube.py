#!/usr/bin/env python

import spiceypy as spice
import math
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = 5013249900
import argparse
import glob
from scipy.misc import imresize

from sciimg.isis3 import info
from sciimg.isis3 import scripting
from sciimg.isis3 import importexport
from sciimg.isis3 import _core

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


class Texture:

    def __init__(self, cube_file=None):
        self.__cube_file = cube_file
        self.__tiff_file = self.cube_to_tiff(cube_file)
        self.__tex_id = None

    def is_loaded(self):
        return self.__tex_id is not None

    def load(self):
        if self.is_loaded():
            return
        self.load_texture(self.__tiff_file, from16bitTiff=True)

    def unload(self):
        if not self.is_loaded():
            return

        # Delete the textures outright. Be rid of the memory
        glDeleteTextures(1, (self.__tex_id,))
        self.__tex_id = None

    def bind(self):
        self.load()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.__tex_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)


    def cube_to_tiff(self, cube_file):

        source_dirname = os.path.dirname(cube_file)
        if source_dirname == "":
            source_dirname = "."

        work_dir = "%s/work" % source_dirname
        if not os.path.exists(work_dir):
            os.mkdir(work_dir)

        bn = os.path.basename(cube_file)

        output_file = "%s/%s.tif" % (work_dir, bn[:-4])
        if os.path.exists(output_file):
            return output_file
        print "Converting", cube_file, "to tiff...",
        importexport.isis2std_grayscale(to_tiff=output_file, from_cube=cube_file)
        print "done"
        return output_file

    def convert_16bitgrayscale_to_8bitRGB(self, im):
        im = np.copy(np.asarray(im, dtype=np.float32))
        im = im / 65535.0
        im = im * 255.0
        im = np.asarray(np.dstack((im, im, im)), dtype=np.uint8)
        return im

    def downscale_texture(self, img, max_dimension=16384):

        if img.shape[0] > max_dimension or img.shape[1] > max_dimension:
            print "Size Before:", img.shape
            ratio = min(float(max_dimension) / float(img.shape[0]), float(max_dimension) / float(img.shape[1]))
            resize_to = (int(img.shape[0] * ratio), int(img.shape[1] * ratio))
            img = imresize(img, resize_to, interp='bilinear')
            print "Size After:", img.shape
            return img
        else:
            return img

    def get_max_texture_size(self):
        print glGetIntegerv(GL_MAX_TEXTURE_SIZE, 0)

    def pillow_to_gl_texture(self, image, from16bitTiff=False):
        if from16bitTiff:
            im = self.convert_16bitgrayscale_to_8bitRGB(image)
            im = self.downscale_texture(im, max_dimension=16384)
            im = Image.fromarray(im)
            ix = im.size[0]
            iy = im.size[1]
            image = im.tobytes("raw", "RGBX", 0, -1)
        else:
            ix = image.size[0]
            iy = image.size[1]
            image = image.tobytes("raw", "RGBX", 0, -1)

        return image, ix, iy

    def load_texture(self, name, from16bitTiff=False):
        if self.__tex_id is not None:
            return
        print "Loading texture '", name, "...",

        # global texture
        image = Image.open(name)
        image, ix, iy = self.pillow_to_gl_texture(image, from16bitTiff)

        # Create Texture
        self.__tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.__tex_id )  # 2d texture (x and y size)

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        print "Done"
        return self.__tex_id


class Model:

    def __init__(self, cube_file, label_file):
        self.__cube_file = cube_file
        self.__label_file = label_file
        self.__texture = Texture(cube_file)

        self.image_time = info.get_field_value(self.__label_file, "IMAGE_TIME")
        self.interframe_delay = float(info.get_field_value(self.__label_file, "INTERFRAME_DELAY"))

        self.start_time = spice.str2et(info.get_field_value(self.__label_file, "START_TIME"))
        self.stop_time = spice.str2et(info.get_field_value(self.__label_file, "STOP_TIME"))
        self.mid_time = (self.start_time + self.stop_time) / 2.0

        self.num_lines = info.get_field_value(self.__label_file, "LINES")

        self.min_lat = float(scripting.getkey(self.__cube_file, "MinimumLatitude", grpname="Mapping"))
        self.max_lat = float(scripting.getkey(self.__cube_file, "MaximumLatitude", grpname="Mapping"))
        self.min_lon = float(scripting.getkey(self.__cube_file, "MinimumLongitude", grpname="Mapping"))
        self.max_lon = float(scripting.getkey(self.__cube_file, "MaximumLongitude", grpname="Mapping"))

        self.__model_output = "%s_rendered.tif"%(self.__cube_file[:-4])
        self.__program_id = None

    def unload_textures(self):
        self.__texture.unload()

    def get_model_output_filename(self):
        return self.__model_output

    @staticmethod
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

    @staticmethod
    def radians_xyz_to_degrees_xyz(xyz):
        return np.array([math.degrees(xyz[0]), math.degrees(xyz[1]), math.degrees(xyz[2])])

    def calculate_orientations(self, frame_number=0):
        et = self.mid_time
        et = et + (frame_number * self.interframe_delay)
        jupiter_state, lt = spice.spkpos('JUPITER', et, 'IAU_SUN', 'NONE', 'SUN')
        jupiter_state = np.array(jupiter_state)

        spacecraft_state, lt = spice.spkpos('JUNO_SPACECRAFT', et, 'IAU_JUPITER', 'NONE', 'JUPITER')
        spacecraft_state = np.array(spacecraft_state)

        m = spice.pxform("IAU_JUPITER", "J2000", et)
        jupiter_rotation = np.array(
            ((m[0][0], m[0][1], m[0][2], 0.0),
             (m[1][0], m[1][1], m[1][2], 0.0),
             (m[2][0], m[2][1], m[2][2], 0.0),
             (0.0, 0.0, 0.0, 1.0))
        )

        m = spice.pxform("JUNO_SPACECRAFT", "IAU_JUPITER", et)
        spacecraft_orientation = np.array(
            ((m[0][0], m[0][1], m[0][2], 0.0),
             (m[1][0], m[1][1], m[1][2], 0.0),
             (m[2][0], m[2][1], m[2][2], 0.0),
             (0.0, 0.0, 0.0, 1.0))
        )

        m = spice.pxform("JUNO_JUNOCAM_CUBE", "JUNO_SPACECRAFT", et)
        instrument_cube_orientation = np.array(
            ((m[0][0], m[0][1], m[0][2], 0.0),
             (m[1][0], m[1][1], m[1][2], 0.0),
             (m[2][0], m[2][1], m[2][2], 0.0),
             (0.0, 0.0, 0.0, 1.0))
        )

        m = spice.pxform("JUNO_JUNOCAM", "JUNO_JUNOCAM_CUBE", et)
        instrument_orientation = np.array(
            ((m[0][0], m[0][1], m[0][2], 0.0),
             (m[1][0], m[1][1], m[1][2], 0.0),
             (m[2][0], m[2][1], m[2][2], 0.0),
             (0.0, 0.0, 0.0, 1.0))
        )

        return spacecraft_orientation, jupiter_state, spacecraft_state, jupiter_rotation, instrument_cube_orientation, instrument_orientation


    def is_framebuffer_ready(self):
        return glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE

    def render(self, frame_number, rotate_x, rotate_y, rotate_z):
        spacecraft_orientation, jupiter_state, spacecraft_state, jupiter_rotation, instrument_cube_orientation, instrument_orientation = self.calculate_orientations(
            frame_number=frame_number)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        lighting = False

        if lighting is True:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            light_position = (-jupiter_state[0], -jupiter_state[1], -jupiter_state[2])
            glLightfv(GL_LIGHT0, GL_POSITION, light_position, 0);
            glShadeModel(GL_SMOOTH);
            glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0), 0)
        else:
            glDisable(GL_LIGHTING)

        glRotatef(rotate_x, 1, 0, 0)
        glRotatef(rotate_y, 0, 1, 0)
        glRotatef(rotate_z, 0, 0, 1)

        glMultMatrixf(instrument_orientation)
        glMultMatrixf(instrument_cube_orientation)
        glMultMatrixf(spacecraft_orientation)

        glTranslatef(-spacecraft_state[0], -spacecraft_state[1], -spacecraft_state[2])

        glPushMatrix()

        self.draw_image_spherical()

        glPopMatrix()

    @staticmethod
    def normalize_vector(vec):
        l = math.sqrt(math.pow(vec[0], 2) + math.pow(vec[1], 2) + math.pow(vec[2], 2))
        if l == 0.0:
            l = 1.0
        return vec[0] / l, vec[1] / l, vec[2] / l

    @staticmethod
    def calc_surface_normal(v0, v1, v2):
        v0 = np.array(v0)
        v1 = np.array(v1)
        v2 = np.array(v2)

        U = v1 - v0
        V = v2 - v1

        c = np.cross(U, V)
        n = Model.normalize_vector(c)
        return n


    def draw_image_spherical(self, lat_slices=128, lon_slices=128):

        if self.__program_id is None:
            self.__program_id = glGenLists(1)
            glNewList(self.__program_id, GL_COMPILE)
            lat_res = (self.max_lat - self.min_lat) / float(lat_slices)
            lon_res = (self.max_lon - self.min_lon) / float(lon_slices)

            self.__texture.bind()

            for y in range(0, int(lat_slices)):
                glBegin(GL_TRIANGLES)
                for x in range(0, int(lon_slices)):
                    mx_lat = self.max_lat - (lat_res * y)
                    mn_lon = self.min_lon + (lon_res * x)

                    mn_lat = mx_lat - lat_res
                    mx_lon = mn_lon + lon_res

                    mx_lat = math.radians(mx_lat)
                    mn_lat = math.radians(mn_lat)
                    mx_lon = math.radians(mx_lon)
                    mn_lon = math.radians(mn_lon)

                    ul_vector = np.array(spice.srfrec(599, mn_lon, mx_lat))
                    ll_vector = np.array(spice.srfrec(599, mn_lon, mn_lat))
                    ur_vector = np.array(spice.srfrec(599, mx_lon, mx_lat))
                    lr_vector = np.array(spice.srfrec(599, mx_lon, mn_lat))

                    ul_uv = (x / float(lon_slices), 1.0 - y / float(lat_slices))
                    ll_uv = (x / float(lon_slices), 1.0 - (y + 1.0) / float(lat_slices))
                    ur_uv = ((x + 1.0) / float(lon_slices), 1.0 - y / float(lat_slices))
                    lr_uv = ((x + 1.0) / float(lon_slices), 1.0 - (y + 1.0) / float(lat_slices))

                    norm = self.calc_surface_normal(ul_vector, ll_vector, ur_vector)
                    glNormal3f(norm[0], norm[1], norm[2])

                    glTexCoord2f(ul_uv[0], ul_uv[1])
                    glVertex3f(ul_vector[0], ul_vector[1], ul_vector[2])

                    glTexCoord2f(ll_uv[0], ll_uv[1])
                    glVertex3f(ll_vector[0], ll_vector[1], ll_vector[2])

                    glTexCoord2f(ur_uv[0], ur_uv[1])
                    glVertex3f(ur_vector[0], ur_vector[1], ur_vector[2])

                    norm = self.calc_surface_normal(ur_vector, ll_vector, lr_vector)
                    glNormal3f(norm[0], norm[1], norm[2])

                    glTexCoord2f(ur_uv[0], ur_uv[1])
                    glVertex3f(ur_vector[0], ur_vector[1], ur_vector[2])

                    glTexCoord2f(ll_uv[0], ll_uv[1])
                    glVertex3f(ll_vector[0], ll_vector[1], ll_vector[2])

                    glTexCoord2f(lr_uv[0], lr_uv[1])
                    glVertex3f(lr_vector[0], lr_vector[1], lr_vector[2])
                glEnd()
            glEndList()
        glCallList(self.__program_id)


class RenderEngine:

    def __init__(self, cube_file_red, cube_file_green, cube_file_blue, label_file, output_file, output_width, output_height, frame_offset, window_size=(1024, 1024)):
        self.red_model = Model(cube_file_red, label_file)
        self.green_model = Model(cube_file_green, label_file)
        self.blue_model = Model(cube_file_blue, label_file)
        self.output_file = output_file
        self.output_width = output_width
        self.output_height = output_height
        self.__frame_number = frame_offset
        self.__scale = 1.0
        self.__fov = 90
        self.__rotate_x = 0
        self.__rotate_y = 0
        self.__rotate_z = 0
        self.__process_final_and_exit = False
        self.__window_size = window_size

    def reshape(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = float(width) / float(height)
        gluPerspective(self.__fov, aspect, 100, 900000.0)
        glutPostRedisplay()

    def mouse(self, button, state, x, y):
        pass

    def motion(self, x1, y1):
        pass

    def keyboard(self, c, x, y):
        """keyboard callback."""
        if c in ["q", chr(27)]:
            sys.exit(0)
        elif c == 'f':
            self.__frame_number += 1.0
            print self.__frame_number
        elif c == 'F':
            self.__frame_number += 100.0
            print self.__frame_number
        elif c == 'b':
            self.__frame_number -= 1.0
            print self.__frame_number
        elif c == 'B':
            self.__frame_number -= 100.0
            print self.__frame_number
        elif c == 'i':
            self.__scale -= 0.1
        elif c == 'o':
            self.__scale += 0.1
        elif c == 'k':
            self.__fov -= 1.0
            self.reshape(self.__window_size[0], self.__window_size[1])
        elif c == 'l':
            self.__fov += 1.0
            self.reshape(self.__window_size[0], self.__window_size[1])
        elif c == 's':
            self.__rotate_x = 0.0
            self.__rotate_y = 0.0
            self.__rotate_z = 0.0
        elif c == 'w':
            self.__rotate_x += 1.0
        elif c == 'x':
            self.__rotate_x -= 1.0
        elif c == 'a':
            self.__rotate_y += 1.0
        elif c == 'd':
            self.__rotate_y -= 1.0
        elif c == 'e':
            self.__rotate_z += 1.0
        elif c == 'r':
            self.__rotate_z -= 1.0
        elif c == 'p':
            self.__process_final_and_exit = True

        glutPostRedisplay()

    def display_standard(self):
        print "Rendering Grayscale frame with red channel..."
        self.red_model.render(self.__frame_number, self.__rotate_x, self.__rotate_y, self.__rotate_z)
        glFlush()
        glutSwapBuffers()

    @staticmethod
    def create_dummy_image(width, height):
        im = np.zeros((width, height, 4), dtype=np.uint8)
        im = Image.fromarray(im)
        image = im.tobytes("raw", "RGBA", 0, -1)
        return image



    def display_for_export(self):
        self.reshape(self.output_width, self.output_height)

        dummy_image = self.create_dummy_image(self.output_width, self.output_height)

        fb_name = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fb_name)

        fb_tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, fb_tex_id)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.output_width, self.output_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, dummy_image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, fb_tex_id, 0)
        glDrawBuffers(1, GL_COLOR_ATTACHMENT0)

        print "Rendering Red..."
        self.red_model.render(self.__frame_number, self.__rotate_x, self.__rotate_y, self.__rotate_z)
        self.red_model.unload_textures()
        red_pixels = self.export_frame_buffer(self.red_model.get_model_output_filename())

        print "Rendering Green..."
        self.green_model.render(self.__frame_number, self.__rotate_x, self.__rotate_y, self.__rotate_z)
        self.green_model.unload_textures()
        green_pixels = self.export_frame_buffer(self.green_model.get_model_output_filename())

        print "Rendering Blue"
        self.blue_model.render(self.__frame_number, self.__rotate_x, self.__rotate_y, self.__rotate_z)
        self.blue_model.unload_textures()
        blue_pixels = self.export_frame_buffer(self.blue_model.get_model_output_filename())

        print "Building RGB Composite..."
        rgba_buffer = np.zeros(red_pixels.shape, dtype=np.uint8)
        rgba_buffer[:, :, 0] = red_pixels[:,:,1]
        rgba_buffer[:, :, 1] = green_pixels[:, :, 1]
        rgba_buffer[:, :, 2] = blue_pixels[:, :, 1]
        rgba_buffer[:, :, 3] = 255

        self.save_image(self.output_file, rgba_buffer)
        sys.exit(0)

    def export_frame_buffer(self, save_copy_to=None):
        pixels = glReadPixels(0, 0, self.output_width, self.output_height, GL_RGBA, GL_UNSIGNED_BYTE)

        dt = np.dtype(np.uint8)
        dt = dt.newbyteorder('>')
        pixels = np.frombuffer(pixels, dtype=dt)
        pixels = np.flip(np.reshape(pixels, (-1, output_width, 4)), 0)

        if save_copy_to is not None:
            self.save_image(save_copy_to, pixels)

        return pixels

    @staticmethod
    def save_image(path, data):
        im = Image.fromarray(data)
        im.save(path)
        # data_matrix = data.astype(np.uint16) / 255.0 * 65535.0
        # tiff = TIFFimage(data, description='')
        # tiff.write_file(path, compression='none')

    def display(self):
        if self.__process_final_and_exit is True:
            self.display_for_export()
        else:
            self.display_standard()

    def __init_glut(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        glutInitWindowSize(*self.__window_size)
        glutCreateWindow(sys.argv[0])
        glutReshapeFunc(self.reshape)
        glutDisplayFunc(self.display)
        glutKeyboardFunc(self.keyboard)
        glutMouseFunc(self.mouse)
        glutMotionFunc(self.motion)

    def __init_opengl(self):
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_POLYGON_SMOOTH)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_TEXTURE_2D)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glEnable(GL_NORMALIZE)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def main(self):
        self.__init_glut()
        self.__init_opengl()
        return glutMainLoop()




def load_kernels(kernelbase, allow_predicted=False):
    kernels = [
        "%s/juno/kernels/pck/pck00010.tpc"%kernelbase,
        "%s/juno/kernels/fk/juno_v12.tf"%kernelbase,
        "%s/juno/kernels/ik/juno_junocam_v02.ti"%kernelbase,
        "%s/juno/kernels/lsk/naif0012.tls"%kernelbase,
        "%s/juno/kernels/sclk/JNO_SCLKSCET.00074.tsc"%kernelbase,
        "%s/juno/kernels/tspk/de436s.bsp"%kernelbase,
        "%s/juno/kernels/tspk/jup310.bsp"%kernelbase,
        "%s/juno/kernels/spk/juno_struct_v04.bsp"%kernelbase
    ]

    kernel_prefix = "spk_rec_" if not allow_predicted else ""
    for file in glob.glob("%s/juno/kernels/spk/%s*bsp"%(kernelbase, kernel_prefix)):
        kernels.append(file)

    kernel_prefix = "juno_sc_rec_" if not allow_predicted else ""
    for file in glob.glob("%s/juno/kernels/ck/%s*bc"%(kernelbase, kernel_prefix)):
        kernels.append(file)

    for kernel in kernels:
        spice.furnsh(kernel)



if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--red", help="Input Projected JunoCam Image for red (cube formatted)", required=True, type=str)
    parser.add_argument("-g", "--green", help="Input Projected JunoCam Image for green (cube formatted)", required=True,
                        type=str)
    parser.add_argument("-b", "--blue", help="Input Projected JunoCam Image for blue (cube formatted)", required=True,
                        type=str)
    parser.add_argument("-l", "--label", help="Input JunoCam Label File (PVL formatted)", required=True, type=str)
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-k", "--kernelbase", help="Base directory for spice kernels", required=False, type=str, default=os.environ["ISIS3DATA"])
    parser.add_argument("-o", "--output", help="Output file path", required=True, type=str, default=None)
    parser.add_argument("-f", "--frameoffset", help="Frame offset", required=False, type=int, default=0)
    parser.add_argument("-F", "--fov", help="Field of view (degrees)", required=False, type=int, default=90)
    parser.add_argument("-W", "--width", help="Image width in pixels", required=False, type=int, default=2048)
    parser.add_argument("-H", "--height", help="Image height in pixels", required=False, type=int, default=2048)
    parser.add_argument("-s", "--scale", help="Image height in pixels", required=False, type=float, default=1.0)
    parser.add_argument("-p", "--predicted", help="Utilize predicted kernels", action="store_true")

    args = parser.parse_args()

    lbl_file = args.label
    cube_file_red = args.red
    cube_file_green = args.green
    cube_file_blue = args.blue
    verbose = args.verbose
    kernelbase = args.kernelbase
    output = args.output
    frame_offset = args.frameoffset
    output_width = args.width
    output_height = args.height
    scale = args.scale
    allow_predicted = args.predicted

    ratio = min(float(1024) / float(output_width), float(1024) / float(output_height))
    window_size = (int(output_width * ratio), int(output_height * ratio))

    FOV = args.fov
    load_kernels(kernelbase, allow_predicted)

    engine = RenderEngine(cube_file_red, cube_file_green, cube_file_blue, lbl_file, output, output_width, output_height, frame_offset, window_size=window_size)
    sys.exit(engine.main())
