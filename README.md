# convert-to-neuroglancer
- convert images like TIF/NIFTI to neuroglancer's image with precomputed format
- convert images like PNG/NIFTI/GIFTI to neuroglancer's segmentations with precomputed format
- convert excel/csv to neuroglancer's annotations with precomputed format

# Environment
- python3.10
- node20

# Python setup
```
conda create -n pt10 python=3.10
conda activate pt10
conda install zimg -c fenglab
pip install tensorstore fsleyes matplotlib numpy nibabel tqdm vtk
```

# Node setup
```
npm install @ant-design/colors jstat xlsx
```
