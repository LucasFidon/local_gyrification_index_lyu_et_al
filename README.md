# Compute local gyrification indices for fetal brain MRI using the method of Lyu et al.

## Installation
First, get the docker image of the software for computing the local gyrification indices
https://github.com/ilwoolyu/LocalGyrificationIndex

Once docker is installed on your machine, this can be done using the command line:
```bash
docker pull ilwoolyu/cmorph:1.7
```

Second, install VTK python library version 8.1.2

The code has been tested only for
 * Python 3.6
 * VTK python library version 8.1.2
 
## How to compute LGI values using the code
An example of script used to compute LGI values and save them in a CSV file can be found in
```run_batch_lgi.py```.

The output will be saved in the folder defined by the variable ```SAVE_FOLDER```.


## How to visualize the LGI map
The script ```display.py``` can be used to visualize the LGI result.

This can be used using the command line:
```bash
python3.6 display.py --cgm <path-to-cortical-gray-matter-vtk-file> --lgi <path-to-lgi-map-file>
```

##### Assumptions:
* patient ID = study folder name
* segmentations for white matter, cortical gray matter, and corpus callosum are present
* file names of the segmentation must be: parcellation.nii.gz


## How to cite
All the credit for this work goes to the authors of 
https://github.com/ilwoolyu/LocalGyrificationIndex

Check their repository for instructions on how to cite their method.