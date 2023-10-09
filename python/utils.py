import os
from zimg import *

def make_dir(path):
  if not os.path.exists(path):
    os.mkdir(path)

def get_segid(filename):
  return os.path.basename(filename).split(".")[0].lstrip("0")

def resize_image( image, 
                  des_depth: int=0, des_height: int=0, des_width:int=0, 
                  interpolant: Interpolant = Interpolant.Cubic, 
                  antialiasing: bool = True, 
                  antialiasingForNearest: bool = False):
  width = image.shape[-1]
  height = depth = 1
  if image.ndim > 1:
    height = image.shape[-2]
  if image.ndim > 2:
    depth = image.shape[-3]
  
  do_resizing = (des_depth > 0 and des_depth != depth) or \
                  (des_height > 0 and des_height != height) or \
                  (des_width > 0 and des_width != width)
  if do_resizing:               
    img = ZImg(image[np.newaxis, :, :, :])
    img.resize(desWidth=des_width if des_width > 0 else width,
               desHeight=des_height if des_height > 0 else height,
               desDepth=des_depth if des_depth > 0 else depth,
               interpolant=interpolant, 
               antialiasing=antialiasing,
               antialiasingForNearest=antialiasingForNearest)
    return img.data[0][0, :, :, :].copy()
  else:
    return image

