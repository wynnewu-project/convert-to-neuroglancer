import os
from utils import make_dir
import json

sharding = {'@type': 'neuroglancer_uint64_sharded_v1',
                'hash': 'identity',
                'minishard_bits': 6,
                'minishard_index_encoding': 'gzip',
                'data_encoding': 'gzip',
                'preshift_bits': 9,
                'shard_bits': 15}

VOXEL_UNIT = {
  "nm": 1,
  "um": 1e3,
  "mm": 1e6,
  "m": 1e9
}    

def create_segmentation_dir(root_dir):
  root_path = os.path.join(os.getcwd(), root_dir)
  make_dir(root_path)

  mesh_dir = os.path.join(root_path, 'mesh')
  segment_properties_dir = os.path.join(root_path, 'segment_properties')

  make_dir(mesh_dir)
  make_dir(segment_properties_dir)

  with open(f'{mesh_dir}/info', 'w') as mf: 
    json.dump({"@type": "neuroglancer_legacy_mesh"}, mf)
  
  return root_path

def write_segment_properties_info(segment_properties_dir, ids=[], labels=[], colors=[]):
  make_dir(segment_properties_dir)
  segment_properties = {
	  "@type": "neuroglancer_segment_properties", 
	  "inline": {
	  	"ids": ids, 
	  	"properties": [{
	  		"id": "label", 
	  		"type": "label", 
	  		"values": labels
	  	}]
	  }
  }

  with open(f'{segment_properties_dir}/info', 'w') as spf: 
    json.dump(segment_properties, spf)

def write_segmentation_base_info(root_path, resolution, size, data_type="uint32", ):
  info_content = {
    "@type": "neuroglancer_multiscale_volume",
    "data_type": data_type,
    "mesh": "mesh",
    "num_channels": 1,
    "segment_properties": "segment_properties",
    "type": "segmentation",
    "scales": [
      {
        "chunk_sizes": [ [ 64, 64, 64 ] ],
        "compressed_segmentation_block_size": [ 8, 8, 8 ],
        "encoding": "compressed_segmentation",
        "key": "_".join([ str(r) for r in resolution]),
        "resolution": resolution,
        "sharding": {
          "@type": "neuroglancer_uint64_sharded_v1",
          "data_encoding": "gzip",
          "hash": "identity",
          "minishard_bits": 6,
          "minishard_index_encoding": "gzip",
          "preshift_bits": 9,
          "shard_bits": 15
        },
        "size": size,
        "voxel_offset": [ 0, 0, 0 ]
      },
    ]
  }
  with open(f'{root_path}/info', 'w') as f: 
    json.dump(info_content, f)

