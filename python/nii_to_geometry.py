import sys

from vtkmodules.vtkIOImage import vtkNIFTIImageReader
from vtkmodules.vtkFiltersCore import vtkWindowedSincPolyDataFilter
from vtkmodules.vtkFiltersGeneral import vtkMarchingContourFilter 
from vtk.util import numpy_support

from tqdm import tqdm
from pathlib import Path
import os
import json
import numpy as np
from utils import make_dir, get_segid
from zmesh import Mesh
from mesh_handler import mesh_to_precomputed
from nifti_handler import get_image_header 
from precomputed_io import create_segmentation_dir, write_segmentation_base_info, write_segment_properties_info, VOXEL_UNIT
import math


def nii_to_vtkPolyData(nii_file):
  reader = vtkNIFTIImageReader()
  reader.SetFileName(nii_file)
  reader.Update()

  header = reader.GetNIFTIHeader()

  temp = [0] * 16
  qform = reader.GetQFormMatrix()
  qform.DeepCopy(temp, qform)
  qform = np.reshape(temp, (4,4))

  surf = vtkMarchingContourFilter()
  surf.SetInputConnection(reader.GetOutputPort())
  surf.ComputeNormalsOn()
  surf.ComputeGradientsOn()
  surf.ComputeScalarsOn()
  surf.Update()


  #smoothing the mesh
  smoother= vtkWindowedSincPolyDataFilter()
  smoother.SetInputConnection(surf.GetOutputPort())
  smoother.SetNumberOfIterations(12) 
  smoother.SetPassBand(0.001)
  smoother.NonManifoldSmoothingOn()
  smoother.NormalizeCoordinatesOn()
  smoother.BoundarySmoothingOn()
  smoother.FeatureEdgeSmoothingOn()
  smoother.SetFeatureAngle(120)
  smoother.Update() 

  return [ smoother, qform]


def nii_to_vertice_and_faces(nii_file):
  vtk_obj, qform = nii_to_vtkPolyData(nii_file)

  vtk_ploy_data = vtk_obj.GetOutput()
  polys = vtk_ploy_data.GetPolys().GetConnectivityArray()
  faces = np.reshape(numpy_support.vtk_to_numpy(polys), (-1,3))

  points = vtk_ploy_data.GetPoints().GetData()
  vertices = numpy_support.vtk_to_numpy(points)
  mat = [qform[0,0], qform[1,1], qform[2, 2]]
  translation = qform[:3, 3]
  vertices *= mat
  vertices += translation

  return [vertices, faces]

def nii_to_obj(nii_file, target_dir, segid=None):
  if not segid:
    segid = get_segid(nii_file)
  make_dir(target_dir)
  vertices, faces = nii_to_vertice_and_faces(nii_file)
  mesh = Mesh(vertices, faces, [])
  with open(f'{target_dir}/{segid}.obj', 'wb') as f:
    f.write(mesh.to_obj())

def nii_to_obj_batch(nii_dir, obj_dir):
  nii_folder = Path(nii_dir)
  for nii_file in tqdm(nii_folder.glob("*.nii.gz"), total=len(list(nii_folder.glob("*.nii.gz"))), desc="Loading Nifti Files"):
    nii_to_obj(nii_file, obj_dir)


def convert_niftis_to_precomputed_mesh(nii_dir, target_dir, need_generate_info=True):
  create_segmentation_dir(target_dir)
  nii_folder = Path(nii_dir)
  ids = []
  init_base_info = False
  for nii_file in tqdm(nii_folder.glob("*.nii.gz"), total=len(list(nii_folder.glob("*.nii.gz"))), desc="Loading Nifti Files"):
    segid = get_segid(nii_file)
    vertices, faces = nii_to_vertice_and_faces(nii_file)
    image_info = get_image_header(nii_file)
    if not init_base_info and need_generate_info:
      write_segmentation_base_info(target_dir, image_info['resolution'], image_info['shape'])
      init_base_info = True
    mesh_to_precomputed(
      f'{target_dir}/mesh',
      segid,
      vertices,
      faces,
      image_resolution=[VOXEL_UNIT[image_info['xyz_units']]] * 3,
      image_offset=image_info['offset']
    )
    ids.append(segid)
  write_segment_properties_info(f'{target_dir}/segment_properties', ids=ids, labels=ids)



if __name__ == "__main__":
  nii_dir = sys.argv[1]
  target_dir = sys.argv[2]

  convert_niftis_to_precomputed_mesh(nii_dir, target_dir)
