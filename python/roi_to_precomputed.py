import os
import sys
import numpy as np
import json
import math
from utils import make_dir
from roi_to_precomputed_sliceview import roi_to_precomputed_sliceview
from nii_to_geometry import convert_niftis_to_precomputed_mesh

"""
atlas:
- image_size                  
- image_resolution
- image_offset
- roi_dir 
- layer_name
"""

def segments_to_precomputed(atlas):
  image_size = atlas["image_size"]
  image_resolution = atlas["image_resolution"]
  roi_dir = atlas["roi_dir"]
  layer_name = atlas["layer_name"]
  out_folder = f'{os.getcwd()}/{layer_name}'

  make_dir(out_folder)

  roi_to_precomputed_sliceview(roi_dir, image_size, image_resolution, out_folder, layer_name)
  convert_niftis_to_precomputed_mesh(roi_dir, out_folder, need_generate_info=False)

  with open(f'{out_folder}/info') as f:
    info_content = json.load(f)
    info_content["mesh"] = "mesh"
    info_content["segment_properties"] = "segment_properties"
  with open(f'{out_folder}/info', 'w') as newf:
    json.dump(info_content, newf)

if __name__ == "__main__":
  atlas = {}
  # brainnetome
  #atlas["image_size"] = [146, 175, 146]
  #atlas["image_resolution"] = [1250000, 1250000, 1250000]
  #atlas["roi_dir"] = "/home/wynne/atlas/brainnetome/ROI_mask/ROI_mask"
  #atlas["layer_name"] = "bn_atlas_regions"

  # allen_ccf
  #atlas["image_size"] = [1320, 800, 1140]
  #atlas["image_resolution"] = [10000000, 10000000, 10000000]
  #atlas["roi_dir"] = "/home/wynne/atlas/allen_institute/mask"
  #atlas["layer_name"] = "allen_ccf_regions"

  # macaque
  atlas["image_size"] = [201, 268, 171]
  atlas["image_resolution"] = [300000, 300000, 300000]
  atlas["roi_dir"] = sys.argv[1]
  atlas["layer_name"] = "macaque_bna_regions"
  atlas["image_offset"] = [-30, -47, -22]

  segments_to_precomputed(atlas)




