# Install

```
npm install
```

# Convert
|Target Annotation Type|Type description|Scripts|Remark|
|---|---|---|---|
|AXIS_ALIGNED_BOUNDING_BOX|box|boxAnnotations.mjs||
|ELLIPSOID|ellipsoid aligned with axes|ellipsoidAnnotations.mjs||
|LINE|line|lineAnnotations.mjs||
|AtlasEllipsoid|ellipsoid not aligned with axes|atlasEllipsoidAnnotation.mjs|Need using in vue application with @feng-lab/vue-neuroglancer and @feng-lab/neuroglancer|
|SPHERE|spheres|sphereAnnotations.mjs|Better performance than POINT|

# How to use 

```
node [scripts] [options]

Required options:
--infoFile: File path to store the defined information of annotations 
--resolution: resolution in unit 'm'
--upperBound: Array of numbers of length rank specifying the exclusive upper bound.All annotation geometry should be contained within the bounding box defined by lower_bound and upper_bound.

Optional Options:
--lowerBound: Array of numbers of length rank specifying the lower bound. Default is [0,0,0]
--targetDir: Output folder.Default is annotaion_${type}
--generateIndex: Whether to generate encoded respresentation for each single annotation and save it in a separate file. It will be used by Neuroglancer when selecting or hovering over an annotation. Default is false.
```

# Support file format
- Excel(*.xlsx, *.xls)
- CSV
- TXT

# File content format
Each row in the info file represents an annotation.\
Each row has the same amount of the data.\
In CSV and TXT files, the following symbols can be used to separate the datas in each row:
',', ' ', '|', '\t'

### AXIS_ALIGNED_BOUNDING_BOX
You need to provide the positions of the two vertices on the box for each annotation.
The first position followed by the second position.

**Format of each line:**

|Datas|x1|y1|z1|x2|y2|z2|
|---|---|---|---|---|---|---|
|Required|Y|Y|Y|Y|Y|Y|

- The first position is (x1, y1, z1)
- The second position is (x2, y2, z2)

**Examples:**

```
# two vertices is (0, 0, 0) and (1, 1, 1)
0 0 0 1 1 1

# Use other delimiters
0,0,0,1,1,1
0|0|0|1|1|1
0\t0\t0\t1\t1\t1

```

### ELLIPSOID
You need to provide a center position and radii vector for each ellipsoid.
- You can use --radii=number to specify each element in the vector when executing the script. For example, --radii=5 means that the radii vector is (5, 5, 5)
- You can define the radii vector for each ellipsoid in the infoFile like.
If the radii vector is not explicitly defined, the default value is to be used.

**Format of each line:**

||x|y|z|radii_x|radii_y|radii_z|red|green|blue|alpha|
|---|---|---|---|---|---|---|---|---|---|---|
|Required|Y|Y|Y||||||||

- (x, y, z) is the center position
- (radii_x, radii_y, radii_z) is the radii vector. Default is (10, 10, 10) 
- (red, green, blue, alpha) is the color(represented as 4 uint8 valuesr) of the ellipsoid. Default is (255, 255, 255, 255)

**Examples:**

```
# center position: (0, 0, 0), radii vector: (10, 10, 10), color:(255, 255, 0, 255)
0,0,0

# center position: (0, 0, 0), radii vector: (20, 10, 5), color:(255, 255, 0, 255)
0,0,0,20,10,5

# center position: (0, 0, 0), radii vector: (20, 10, 5), color:(128, 133, 144, 255)
0,0,0,20,10,5,128,133,144

# center position: (0, 0, 0), radii vector: (20, 10, 5), color:(128, 133, 144, 178)
0,0,0,20,10,5,128,133,144,178

# center position: (0, 0, 0), radii vector: (10, 10, 10), color:(128, 133, 144, 178)
# If you want to specify a color but use the default radius size, the radius vector value can be empty or 0, but must be provided.
0,0,0,,,,128,133,144,178
0 0 0    128 133 144 178
0|0|0||||128,133,144,178
0\t0\t0\t\t\t\t128\t133\t144\t178
```

### LINE
You need to provide the two endpoint positions for each line.\
You can customize the width and color of each line.

**Format of each line:**

||x1|y1|z1|x2|y2|z2|width|red|green|blue|alpha|
|---|---|---|---|---|---|---|---|---|---|---|---
|Required|Y|Y|Y|Y|Y|Y|||||

- The first endpoint is (x1, y1, z1), and the second is (x2, y2, z2)
- The unit of line width is one screen pixel. Default is 1.
- (red, green, blue, alpha) is the color(represented as 4 uint8 valuesr) of the line. Default is (255, 255, 0, 255)

**Examples:**

```
# two endpoints: (0,0,0) and (1,1,1), line width: 1, line color: (255,255,0,255)
0,0,0,1,1,1

# two endpoints: (0,0,0) and (1,1,1), line width: 3, line color: (255,255,0,255)
0,0,0,1,1,1,3

# two endpoints: (0,0,0) and (1,1,1), line width: 3, line color: (133,144,148,233)
0,0,0,1,1,1,3,133,144,148,233

# two endpoints: (0,0,0) and (1,1,1), line width: 1, line color: (133,144,148,233)
# If you want to specify a color but use the default width, the width should be empty or 0
0,0,0,1,1,1,,133,144,148,233
0 0 0 1 1 1  133 144 148 233
0|0|0|1|1|1||133|144|148|233
0\t0\t0\t1\t1\t1\t\t133\t144\t148\t233
```

### AtlasEllipsoid
You can drawing a ellipsoid not aligned with axes.\
You need to provide a center position and the angles of rotation of the three axes of the ellipsoid.Each angle is represented by a three-dimensional variable

**Format of each line:**

||x|y|z|x-axis_angle_x|x-axis_angle_y|x-axis_angle_z|y-axis_angle_x|y-axis_angle_y|y-axis_angle_z|z-axis_angle_x|z-axis_angle_y|z-axis_angle_z|
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|Required|Y|Y|Y|Y|Y|Y|Y|Y|Y|Y|Y|Y|

- The center position is (x, y, z)
- The rotation of the x-axis of the ellipsoid is (x-axis_angle_x, x-axis_angle_y, x-axis_angle_z)
- The rotation of the y-axis of the ellipsoid is (y-axis_angle_x, y-axis_angle_y, y-axis_angle_z)
- The rotation of the z-axis of the ellipsoid is (z-axis_angle_x, z-axis_angle_y, z-axis_angle_z)

**Examples:**

```
# center: (0,0,0)
# rotation angle:  x-axis(2, 3, 4), y-axis(5,6,7), z-axis(8,9,10)
0,0,0,2,3,4,5,6,7,8,9,10

# center: (0,0,0)
# aligned with axes
0,0,0,1,0,0,0,1,0,0,0,1
```

### SPHERE
You can drawing a spheres.\
You need to provide a center position at least.\
You can customize the radius and color of spheres. 

**Format of each line:**

||x|y|z|radius|red|green|blue|alpha|
|---|---|---|---|---|---|---|---|---|
|Required|Y|Y|Y|Y||||

- The center position: (x, y, z)
- The unit of radius is 1 in the coordinate system at the current resolution
- (red, green, blue, alpha) is the color(represented as 4 uint8 valuesr) of the spheres. Default is (255, 255, 0, 255)

**Examples:**

```
# center: (0, 0, 0), radius: 5
0 0 0 5 

# center: (0, 0, 0), radius: 5, color(133, 144, 148, 255)
0 0 0 5 133 144 148

# center: (0, 0, 0), radius: 5, color(133, 144, 148, 128)
0 0 0 5 133 144 148 128
```













