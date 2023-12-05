import os
from utils import make_dir, get_segid
from zimg import *
import numpy as np
from neuroglancer_scripts.dyadic_pyramid import fill_scales_for_dyadic_pyramid
import tensorstore as ts
import math
import sys
from precomputed_io import write_segment_properties_info, VOXEL_UNIT, sharding
import argparse
import json

def parse_command_line(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument("image")
  parser.add_argument("-r", default=[1,1,1])
  parser.add_argument("-d", default="")
  parser.add_argument("-width", default=0)
  parser.add_argument("-height", default=0)
  args = parser.parse_args(argv[1:])
  return args



def labeled_image_to_precomputed(png_file, fullres_resolution=[1,1,1], target_dir="", destWidth=0, destHeight=0):
  root_path = os.path.join(os.getcwd(), target_dir)
  make_dir(root_path)

  raw_img = img = ZImg(png_file)

  img_data = raw_img.data[0]


  if destWidth != 0 or destHeight != 0:
    print("need resize")
    raw_img = img.resize(desWidth=destWidth, 
                         desHeight=destHeight,
                         desDepth=img.info.depth,
                         interpolant=Interpolant.Nearest, 
                         antialiasing=True, 
                         antialiasingForNearest=False)
          
  img_info = raw_img.info

  img_data = raw_img.data[0]
  ids = [ str(id) for id in list(np.unique(img_data[np.nonzero(img_data)])) ]
  fullres_info = {}
  fullres_info['type'] = 'segmentation'
  fullres_info['data_type'] = img_info.dataTypeString()
  fullres_info['num_channels'] = 1 
  fullres = {}
  fullres['chunk_sizes'] = []
  fullres['encoding'] = 'raw'
  fullres['sharding'] = sharding
  fullres['resolution'] = fullres_resolution
  fullres['size'] = [img_info.width, img_info.height, img_info.depth]
  fullres['voxel_offset'] = [0, 0, 0]
  fullres_info['scales'] = [fullres, ]
  fill_scales_for_dyadic_pyramid(fullres_info, target_chunk_size=64)

  start_ch = 1e10
  end_ch = -1
  for scale in fullres_info['scales']:
    scale['chunk_size'] = scale['chunk_sizes'][0]
    del scale['chunk_sizes']
    scale['key'] = '_'.join([str(r) for r in scale['resolution']])
    arrs = {}

    for ch in range(img_info.numChannels):
      start_ch = min(start_ch, ch)
      end_ch = max(end_ch, ch)
      spec = {
        'context': {
          "data_copy_concurrency": {"limit": 10}
        },
        'driver': 'neuroglancer_precomputed',
        'kvstore': {'driver': 'file', 'path': root_path},
        'path': f'channel_{ch}', 
        'scale_metadata': scale,
        'multiscale_metadata': {
          'data_type': fullres_info['data_type'],
          'num_channels': fullres_info['num_channels'],
          'type': fullres_info['type'],
        }
      }
      arrs[ch] = ts.open(spec=spec, open=True, create=True).result()


    xRatio = round(scale['resolution'][0] / fullres['resolution'][0])
    yRatio = round(scale['resolution'][1] / fullres['resolution'][1])
    zRatio = round(scale['resolution'][2] / fullres['resolution'][2])

    _resize_img = ZImg(img_data)

    if not (xRatio == 1 and yRatio == 1 and zRatio == 1):
      _resize_img = _resize_img.resize(desWidth=scale['size'][0],
                                       desHeight=scale['size'][1],
                                       desDepth=scale['size'][2],
                                       interpolant=Interpolant.Nearest,
                                       antialiasing=True,
                                       antialiasingForNearest=False
                                       )
    _img_data = _resize_img.data[0]

    save_step = scale['chunk_size'][2] * 2
    slices = [slice(idx * save_step, min(_resize_img.info.depth, save_step * (idx + 1)), 1) for idx in range((_resize_img.info.depth + save_step - 1) // save_step)]
        


    for sl in slices:
      for ch in range(img_info.numChannels): 
        ch_img_data = _img_data[ch - start_ch]
        ravel_data = np.ravel(ch_img_data, order='C')
        reshape_data = np.reshape(ravel_data, (ch_img_data.shape[-1], ch_img_data.shape[-2], ch_img_data.shape[-3]), order='F')
        del ravel_data
        x_step = 1000
        x_slice_num = math.ceil(reshape_data.shape[0] / x_step)
        for i in range(x_slice_num):
          x_start = i * x_step
          x_end = min((i+1) * x_step, reshape_data.shape[0])
          arrs[ch][ts.d['channel'][0]][x_start:x_end, :, sl.start:sl.stop] = reshape_data[x_start:x_end, :, sl.start:sl.stop]
  
  for ch in range(img_info.numChannels):
    ch_root_path = f'{root_path}/channel_{ch}'
    with open(f'{ch_root_path}/info') as infoF: 
      info = json.load(infoF)
      infoF.close()
    info['segment_properties'] = 'segment_properties'
    with open(f'{ch_root_path}/info', 'w') as infoF: 
      json.dump(info, infoF)
    segment_properties_dir = f'{ch_root_path}/segment_properties'
    write_segment_properties_info(segment_properties_dir, ids=ids, labels=ids)
  
if __name__ == "__main__":
  args = parse_command_line(sys.argv)
  args.r = [float(x) for x in args.r.split(',')] 
  labeled_image_to_precomputed(
    args.image, 
    fullres_resolution=args.r,
    target_dir=args.d, 
    destWidth=args.width, 
    destHeight=args.height)

