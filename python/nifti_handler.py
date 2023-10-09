import nibabel as nib
import sys
import os
import numpy as np
from pathlib import Path
from tqdm import tqdm
import numpy as np
import math
from utils import get_segid

NIFTI_UNITS_RESOLUTION = {
  "nm": 1,
  "um": 1E3,
  "mm": 1E6,
  "m": 1E9
}

def get_image_offset(image_file):
  image = nib.load(image_file)
  image_hdr = image.header
  affine = image_hdr.get_best_affine()
  return [affine[0][3], affine[1][3], affine[2][3]]

def get_image_size(image_file):
  image = nib.load(image_file)
  return list(image.header.get_data_shape())

def get_image_resolution(image_file):
  image = nib.load(image_file)
  image_hdr = image.header
  _resolution = image_hdr.get_zooms()
  resolution_units = image_hdr.get_xyzt_units()[0]
  return [ r * NIFTI_UNITS_RESOLUTION[resolution_units] for r in _resolution]

def get_image_header(image_file):
  image = nib.load(image_file)
  image_hdr = image.header
  affine = image_hdr.get_best_affine();
  rank = image_hdr['dim'][0]
  scale = image_hdr.get_zooms()
  xyz_units, time_units = image_hdr.get_xyzt_units();
  return {
    'pixdim': image_hdr['pixdim'],
    'shape': image_hdr.get_data_shape(),
    'rank': rank,
    'scaleMat': affine[:rank, :rank],
    'scale': scale,
    'offset': affine[:rank, rank],
    'xyz_units': xyz_units,
    'time_units': time_units,
    'data_type': image_hdr.get_data_dtype(),
    'resolution': [ r * NIFTI_UNITS_RESOLUTION[xyz_units] for r in scale]
  }


def read_image(image_file):
  image_info = get_image_header(image_file)
  for k, v in image_info.items():
    if k == "scaleMat":  
      print(f'{k}:\n{v}') 
    else: 
      print(f'{k}: {v}')


def read_image_batch(path, regular):
  image_folder = Path(path)
  max_width = 0
  max_height= 0
  max_depth = 0

  for file in tqdm(image_folder.glob(regular), total=len(list(image_folder.glob(regular))), desc="Loading Nifti File"): 
    read_image(file)

def flip_image(image_file):
  image = nib.load(image_file)
  image_data = image.get_fdata()
  newImage = nib.Nifti1Image(np.flipud(image_data), image.affine, dtype="float32")
  newImage.header.set_xyzt_units(xyz="mm")
  nib.save(newImage, "newImage.nii.gz")
  print(newImage.header)

def mask_by_region_id(filePath):   
  segid = segid(filePath)
  region_mask_image = nib.load(filePath)   
  image_x, image_y, image_z = region_mask_image.shape   
  nparray=np.zeros(shape=(image_x, image_y, image_z), dtype=np.uint32)   
  subarr = region_mask_image.dataobj[:,:,:]   
  nparray[:image_x, :image_y, :image_z] += np.where(subarr>0, segid, subarr) 
  with open(f"./{segid}.npy", "wb") as region_f:
  	np.save(region_f, nparray)


    

if __name__ == "__main__":
  path = sys.argv[1]
  read_mode = sys.argv[2]
  if(read_mode == "file"):
    read_image(path)
  else:
    file_regular = sys.argv[3]
    read_image_batch(path, file_regular)


