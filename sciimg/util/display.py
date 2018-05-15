import PIL
from PIL import Image

def disp(img_file):
    display(PIL.Image.open(img_file).convert("RGBA"))