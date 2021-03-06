"""
This script is for converting the segmentations from nifti to vtk format.

TESTED ONLY WITH PYTHON 3.6 AND PYTHON-VTK VERSION 8.1.2
"""

import os
import nibabel as nib
import vtk  # should be version 8.1.2
import numpy as np
from scipy.ndimage.measurements import label


ROI = {
    'wm': 1,
    'in-csf': 2,
    'cer': 3,
    'ext-csf': 4,
    'cgm': 5,
    'dgm': 6,
    'bs': 7,
    'cc': 8,
}


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


def find_where_to_split(cc_mask):
    # We define the plane between right and left as the middle of the CC
    x, _, _ = np.where(cc_mask == 1)
    x_split = round(np.median(x))
    return x_split

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

    cgm = np.copy(seg_array)
    cgm[seg_array == ROI['ext-csf']] = 0
    cgm[seg_array == ROI['cer']] = 0
    cgm[seg_array == ROI['bs']] = 0
    cgm[cgm >= 1] = 1

    # Remove the fourth ventricle and aqueduct
    # For this we use an heuristic:
    # We keep only 2D components that are large enough in each frontal plane
    COMP_THRES = 300
    _, y_vent, _ = np.where(seg_array == ROI['in-csf'])
    for y in range(np.min(y_vent), np.max(y_vent) + 1):
        cor_slice = cgm[:, y, :]
        structure = np.ones((3, 3), dtype=np.int)
        labeled, ncomp = label(cor_slice, structure)
        if ncomp == 0:
            continue
        size_comp = [
            np.sum(labeled == l) for l in range(1, ncomp + 1)
        ]
        # print(size_comp)
        for i in range(1, ncomp + 1):
            if size_comp[i-1] < COMP_THRES:
                labeled[labeled == i] = 0
        labeled[labeled > 0] = 1
        cgm[:, y, :] = labeled

    wm = np.copy(cgm)
    wm[seg_array == ROI['cgm']] = 0
    # wm = (seg_array ==  ROI['wm']).copy()
    # cgm = (seg_array ==  ROI['cgm']).copy()
    cc = (seg_array == ROI['cc']).copy()
    x_split = find_where_to_split(cc)
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
