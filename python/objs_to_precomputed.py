from tqdm import tqdm
from pathlib import Path
from zmesh import Mesh
import sys
from utils import get_segid
from precomputed_io import create_segmentation_dir, write_segmentation_base_info, write_segment_properties_info, VOXEL_UNIT
from mesh_handler import mesh_to_precomputed

def convert_objs_to_precomputed_mesh(obj_dir, target_dir, image_size, xyz_units="nm", image_resolution=[1,1,1], image_offset=[0,0,0]):
  obj_folder = Path(obj_dir)
  ids = []
  create_segmentation_dir(target_dir)
  init_base_info = False

  for obj_file in tqdm(obj_folder.glob("*.obj"), total=len(list(obj_folder.glob("*.obj"))), desc="Loading OBJ Files"):
    with open(obj_file, "rt") as f:
        obj = f.read()
    mesh = Mesh.from_obj(obj) 
    segid = get_segid(obj_file)
    ids.append(segid)

    if not init_base_info:
      write_segmentation_base_info(target_dir, image_resolution, image_size)
      init_base_info = True

    mesh_to_precomputed(
      f'{target_dir}/mesh', 
      segid, 
      mesh.vertices, 
      mesh.faces, 
      image_resolution=[VOXEL_UNIT[xyz_units]] * 3,
      image_offset=image_offset
    )
  write_segment_properties_info(f'{target_dir}/segment_properties', ids=ids, labels=ids)

if __name__ == "__main__":
  obj_dir = sys.argv[1]
  target_dir = sys.argv[2]
  image_size = sys.argv[3].split(", ")
  xyz_units = sys.argv[4]
  image_resolution = sys.argv[5].split(", ")
  image_offset = sys.argv[6].split(", ")

  convert_objs_to_precomputed_mesh(
    obj_dir,
    target_dir,
    image_size,
    xyz_units,
    image_resolution,
    image_offset
  )