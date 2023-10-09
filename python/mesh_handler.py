import json
import numpy as np


def mesh_to_precomputed(mesh_dir, segid, vertices, faces, colors=[], image_offset=[0, 0, 0], image_resolution=[1,1,1]):
  _vertices = vertices.copy()
  _vertices -= np.array(image_offset, dtype=np.float32)
  _vertices *= np.array(image_resolution, dtype=np.float32)
  
  precomputed_format = [
    np.uint32(_vertices.shape[0]),
    _vertices
  ]

  if len(colors):
    precomputed_format.append(np.asarray(colors, dtype=np.float32))
  precomputed_format.append(np.asarray(faces, dtype=np.uint32))



  with open(f'{mesh_dir}/{segid}', "wb") as mesh_file:
    content = b''.join([ array.tobytes('C') for array in precomputed_format])
    mesh_file.write(content)
  with open(f'{mesh_dir}/{segid}:0', "w", encoding="UTF-8") as mesh_info_file:
    info_content = {"fragments": [str(segid)]}
    if len(colors):
      info_content["customColor"] = True
    json.dump(info_content, mesh_info_file) 
