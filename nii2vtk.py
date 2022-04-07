"""
This script is for converting the segmentations from nifti to vtk format.
"""

import os
import nibabel as nib
import vtk  # should be version 8.1.2
from scipy.ndimage.measurements import label
import numpy as np

# TESTED ONLY WITH PYTHON 3.6

ROI = {'wm': 1, 'cgm': 5, 'cc': 8}


def nii2vtk(binary_mask_nii_path, save_path):
    """
    Simple conversion from nifti to vtk format
    for a binary segmentation mask.
    """
    # Read the image
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(binary_mask_nii_path)
    reader.Update()
    image = reader.GetOutput()

    # Set the origin
    nifti = nib.load(binary_mask_nii_path)
    origin = nifti.affine[:3, 3]
    new_origin = [origin[0], origin[1], origin[2]]
    image.SetOrigin(new_origin)

    # Get the contour / isosurface
    contour = vtk.vtkMarchingCubes()
    contour.SetInputData(image)
    contour.ComputeNormalsOn()
    contour.ComputeGradientsOn()
    contour.SetValue(0, 1)
    contour.Update()

    writer = vtk.vtkPolyDataWriter()
    writer.SetInputConnection(contour.GetOutputPort())
    writer.SetFileName(save_path)
    writer.Write()


def find_where_to_split(wm_mask):
    # Find the two largest connected components
    structure = np.ones((3, 3, 3), dtype=np.int)
    labeled, ncomp = label(wm_mask, structure)
    size_comp = [
        np.sum(labeled == l) for l in range(1, ncomp + 1)
    ]
    first_largest_comp = np.argmax(size_comp)
    label_first = first_largest_comp + 1
    size_comp[first_largest_comp] = -1
    second_largest_comp = np.argmax(size_comp)
    label_second = second_largest_comp + 1

    x_1, _, _ = np.where(labeled == label_first)
    x_2, _, _ = np.where(labeled == label_second)
    if np.mean(x_1) > np.mean(x_2):
        x_split = 0.5 * (np.min(x_1) + np.max(x_2))
    else:
        x_split = 0.5 * (np.max(x_1) + np.min(x_2))
    return round(x_split)


# MAIN function
def convert_nii_to_vtk(niftiImagePath, saveFolder):
    def save(roi_mask_array, roi):
        if not os.path.exists(saveFolder):
            os.mkdir(saveFolder)
        roi_mask = nib.Nifti1Image(roi_mask_array, seg.affine, seg.header)
        label_nifti_path = os.path.join(saveFolder, '%s.nii.gz' % roi)
        nib.save(roi_mask, label_nifti_path)
        # Convert it to vtk
        label_vtk_final = os.path.join(saveFolder, '%s.vtk' % roi)
        nii2vtk(label_nifti_path, label_vtk_final)

    # Load the multi-class segmentation
    seg = nib.load(niftiImagePath)
    seg_array = seg.get_fdata()

    wm = (seg_array ==  ROI['wm']).copy()
    cgm = (seg_array ==  ROI['cgm']).copy()
    cc = (seg_array == ROI['cc']).copy()
    x_split = find_where_to_split(wm)
    wm = np.logical_or(wm, cc)

    # Left side
    wm_left = np.copy(wm)
    wm_left[x_split:,:,:] = False
    save(wm_left, 'wm_left')

    cgm_left = np.copy(cgm)
    cgm_left[x_split:,:,:] = False
    save(cgm_left, 'cgm_left')

    # Right side
    wm_right = np.copy(wm)
    wm_right[:x_split,:,:] = False
    save(wm_right, 'wm_right')

    cgm_right = np.copy(cgm)
    cgm_right[:x_split,:,:] = False
    save(cgm_right, 'cgm_right')

        
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Script for conversion from 3D NIfTI images to VTK meshes')
    parser.add_argument('--seg', type=str, help='absolute path to NIfTI image with its name to be converted')
    parser.add_argument('--save', type=str, help="folder where to save the output")

    args = parser.parse_args()
    convert_nii_to_vtk(niftiImagePath=args.seg, saveFolder=args.save)
