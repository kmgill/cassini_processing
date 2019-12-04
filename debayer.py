import numpy as np
import cv2
import sys
from PIL import Image

infile = sys.argv[1]

# TODO Write some actual error checking

img = Image.open(infile)
data = np.copy(np.asarray(img, dtype=np.uint16))
data *= 257
colour = cv2.cvtColor(data, cv2.COLOR_BAYER_BG2BGR)
cv2.imwrite("%s.png"%(infile[:-4]), colour)
