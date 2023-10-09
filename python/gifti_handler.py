import nibabel as nib
import sys
from mesh import mesh_to_precomputed
from precomputed_io import create_segmentation_dir, write_segment_properties_info, write_segmentation_base_info
import json
import matplotlib as mpl
from color_tools import get_colour_map

def parse_surface(surface_file):
  surface_image = nib.load(surface_file)
  vertices = surface_image.agg_data('pointset')
  faces = surface_image.agg_data('triangle')
  return [vertices, faces]


"""
parse the label file(*.gii)

@returns
- label_map: a map that records the color in rgb and name of the brain region using the region ID as the key
- cdata: an array that each element is the label value of the vertex whose id is the index
"""
def parse_label(label_file):
  label_image = nib.load(label_file)
  cdata = label_image.agg_data('label')
  label_map = {}
  label_table = label_image.labeltable
  label_value = label_table.get_labels_as_dict()
  for label in label_table.labels:
    label_map[label.key] = {
      'r': label.red,
      'g': label.green,
      'b': label.blue,
      'a': label.alpha,
      'name': label_value[label.key]
    }
  return [label_map, cdata]


def split_surface_vertices(label_cdata):
  splited_vertices = {}
  vertices_index_map = {}
  for vertice in range(label_cdata.shape[0]):
    owned_label = label_cdata[vertice]
    if owned_label not in splited_vertices:
      splited_vertices[owned_label] = []
    splited_vertices[owned_label].append(vertice)
    vertices_index_map[vertice] = len(splited_vertices[owned_label]) - 1
  return [splited_vertices, vertices_index_map]

def split_surface_faces(faces, splited_vertices, vertices_index_map, label_cdata):
  faces_num = faces.shape[0]
  splited_faces = {}
  cross_vertices_index_map = {}
  splited_vertices['cross'] = []

  def face_join_to_label(owned_label, vertices_in_faces, index_map): 
    if(owned_label == 'cross'):
      for v in vertices_in_faces:
        if v not in index_map:
          splited_vertices['cross'].append(v)
          index_map[v] = len(splited_vertices['cross']) - 1 
    
    if owned_label not in splited_faces:
      splited_faces[owned_label] = []
    
    splited_faces[owned_label].append([index_map[v] for v in vertices_in_faces])
  
  for i in range(faces_num):
    fv = faces[i]
    face_label_set = set([label_cdata[v] for v in fv])
    if(len(face_label_set) == 1):
      face_join_to_label(face_label_set.pop(), fv, vertices_index_map)
    else:
      face_join_to_label('cross', fv, cross_vertices_index_map)
  
  return splited_faces

def generate_label_color_map(label_list, cmap_name, cmap_type):
  vmin = min([int(l) for l in label_list])
  vmax = max([int(l) for l in label_list])
  norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
  color_map = get_colour_map(cmap_name, cmap_type)
  label_color_map = {}
  for label in label_list:
    if label != 0:
      color = color_map(norm(int(label)))
      label_color_map[str(label)] = color[:3]
  label_color_map[str(len(label_list))] = [1.0, 1.0, 1.0]
  return label_color_map



"""
split regions from the surface
each region saved as a single mesh file
"""
def split_surface_with_label(surface_file, label_file, size, resolution=[1,1,1], target_dir="split_gifti"):
  ids = []
  labels = []
  segment_colors = {}

  vertices, faces = parse_surface(surface_file)
  label_map, label_cdata = parse_label(label_file)
  
  splited_vertices, vertices_index_map = split_surface_vertices(label_cdata)
  splited_faces = split_surface_faces(faces, splited_vertices, vertices_index_map, label_cdata)
  root_path = create_segmentation_dir(target_dir)
  label_list = label_map.keys()
  mesh_dir = f'{root_path}/mesh'

  for label in label_list:
    if label != 0 and label in splited_faces:
      label_info = label_map[label]
      vs = [vertices[v] for v in splited_vertices[label]]
      fs = splited_faces[label] 
      ids.append(str(label))
      segment_label = label_info["name"]
      labels.append(segment_label)
      segment_colors[str(label)] = [label_info['r'], label_info['g'], label_info['b']]
      mesh_to_precomputed(mesh_dir, label, vs, fs, image_resolution=resolution)
  
  cross_id = len(label_list)
  mesh_to_precomputed(
    mesh_dir,
    cross_id,
    [vertices[v] for v in splited_vertices['cross']],
    splited_faces['cross'],
    image_resolution=resolution
  )

  segment_colors[str(cross_id)] = [1.0, 1.0, 1.0]


  ids.append(str(cross_id))
  labels.append('cross_region')

  
  write_segment_properties_info(f'{root_path}/segment_properties', ids=ids, labels=labels)
  write_segmentation_base_info(root_path, resolution, size)
  with open(f'{root_path}/state.json', 'w') as f:
    state_content = {
      "segmentColors": segment_colors,
      "segmentColorsType": "vec3"
    }
    json.dump(state_content, f)





if __name__ == "__main__":
  surface_file = sys.argv[1]
  label_file = sys.argv[2]
  target_dir = sys.argv[3]
  resolution = [1000000,1000000,1000000]
  size = [153, 122, 1]
  split_surface_with_label(surface_file, label_file, size, resolution=resolution, target_dir=target_dir)
  