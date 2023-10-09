#!/usr/bin/python
import nibabel as nib
from tqdm import tqdm
from pathlib import Path
import tensorstore as ts
import sys
import os
from neuroglancer_scripts.dyadic_pyramid import fill_scales_for_dyadic_pyramid
import numpy as np
from zimg import *
import time
from multiprocessing import Pool, Lock, Manager
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.managers import SharedMemoryManager
import concurrent.futures
import re
from precomputed_io import sharding
from utils import get_segid, resize_image


def mask_by_region_id(shape, dirname, file, rawArr, segid):
  start_t = time.perf_counter()
  region_mask_image = nib.load(os.path.join(dirname, file))

  region_data = region_mask_image.dataobj[:,:,:]
  image_x, image_y, image_z = region_mask_image.shape
  mask_index = np.where(region_data>0)
  rawArr[mask_index] = segid



def convert_to_precomputed(size, fullres_info, dirname, resolution, out_folder, layer_name):

  rawArr = np.zeros(shape=size, dtype=np.uint32)
  file_list = os.listdir(dirname)

  for roi_file in file_list:
    segid = get_segid(roi_file)
    mask_by_region_id(size, dirname, roi_file, rawArr, segid)

  z_rawArr = np.reshape(np.ravel(rawArr, order="F"), (rawArr.shape[-1], rawArr.shape[-2], rawArr.shape[-3]), order="C")
  for scale in fullres_info['scales']:
    scale['chunk_size'] = scale['chunk_sizes'][0]
    del scale['chunk_sizes']
    scale['key'] = '_'.join(str(x) for x in scale['resolution'])
    print(scale)
    spec = {
      'driver': 'neuroglancer_precomputed',
      'kvstore': {
        'driver': 'file', 
        'path': out_folder
      },
      'path': "",
      'scale_metadata': scale,
      'multiscale_metadata': {
        'data_type': fullres_info['data_type'],
        'num_channels': fullres_info['num_channels'],
        'type': fullres_info['type']
      }
    }
    arr = ts.open(spec=spec, open=True, create=True).result()
    xRatio = round(scale['resolution'][0] / resolution[0])
    yRatio = round(scale['resolution'][1] / resolution[1])
    zRatio = round(scale['resolution'][2] / resolution[2])
    print('radio', xRatio, yRatio, zRatio)
    if xRatio == 1 and yRatio == 1 and zRatio == 1:
      print('current scale', rawArr.shape)
      arr[ts.d['channel'][0]] = rawArr
    else:
      rawArr_for_current_scale = resize_image(
        z_rawArr,
        des_width=(scale['size'][0]),
        des_height=(scale['size'][1]),
        des_depth=(scale['size'][2]),
        interpolant=Interpolant.Nearest)
      print('need reshape:', (rawArr_for_current_scale.shape[2], 
         rawArr_for_current_scale.shape[1], 
         rawArr_for_current_scale.shape[0]))
      arr[ts.d['channel'][0]] = np.reshape(
        np.ravel(rawArr_for_current_scale, order='C'),
        (rawArr_for_current_scale.shape[-1], 
         rawArr_for_current_scale.shape[-2], 
         rawArr_for_current_scale.shape[-3]),
        order="F")

def roi_to_precomputed_sliceview(dirname, size, resolution, out_folder, layer_name):
  fullres_info = {}
  fullres_info['type'] = 'segmentation'
  fullres_info['data_type'] = 'uint32'
  fullres_info['num_channels'] = 1
  fullres = {}
  fullres['chunk_sizes'] = []
  fullres['encoding'] = 'compressed_segmentation'
  fullres['compressed_segmentation_block_size'] = [8, 8, 8]
  fullres['sharding'] = sharding
  fullres['resolution'] = resolution
  fullres['size'] = size
  fullres['voxel_offset'] = [0, 0, 0]
  fullres_info['scales'] = [fullres, ]
  fill_scales_for_dyadic_pyramid(fullres_info, target_chunk_size=64)
  convert_to_precomputed(size, fullres_info, dirname, resolution, out_folder, layer_name)






if __name__ == '__main__':
  dirname = sys.argv[1]
  size = sys.argv[2].split(", ")
  resolution = sys.argv[3].split(", ")
  out_folder = sys.argv[4]
  layer_name = sys.argv[5]
  size = [int(x) for x in size]
  resolution = [float(x) for x in resolution]
  roi_to_precomputed_sliceview(dirname, size, resolution, out_folder, layer_name)










