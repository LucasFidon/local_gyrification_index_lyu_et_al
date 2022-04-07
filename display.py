import os
import vtk
import argparse
import numpy as np
from run_batch_lgi import load_lgi


parser = argparse.ArgumentParser(
    description='Script for coloring a VTK mesh of the cortical gray matter based on the LGI values'
)
parser.add_argument('--cgm', type=str,
                    help='absolute path to VTK mesh of the cortical gray matter for one hemisphere')
parser.add_argument('--lgi', type=str,
                    help='absolute path to the LGI map file')


"""
Tested only with python3.6
"""

def main(cgm_path, lgi_path):

    # Load the mesh
    reader = vtk.vtkPolyDataReader()
    print('Load %s' % cgm_path)
    reader.SetFileName(cgm_path)
    reader.Update()
    mesh = reader.GetOutput()
    nb_points = mesh.GetNumberOfPoints()
    print('The mesh has %d points' % nb_points)

    # Read the LGI
    lgi_np = load_lgi(lgi_path)
    min_lgi = np.nanmin(lgi_np)
    max_lgi = np.nanmax(lgi_np)
    mean_lgi = np.nanmean(lgi_np)
    # lgi_np[np.isnan(lgi_np)] = mean_lgi
    print('Value range: [%f, %f], mean value: %f' % (min_lgi, max_lgi, mean_lgi))
    new_scalars = vtk.vtkFloatArray()
    new_scalars.SetNumberOfTuples(nb_points)
    for i in range(nb_points):
        s = lgi_np[i]
        new_scalars.SetTuple1(i, s)

    # Change scalar attribute of the points
    mesh.GetPointData().SetScalars(new_scalars)

    # LUT
    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.667, 0.0)

    # Mapper: maps dtat into graphics primitives
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mesh)
    mapper.SetScalarModeToUsePointData()
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(1., 3.)  # people usually use 1-5 as range for the LGI

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Every visualization requires a window
    window = vtk.vtkRenderWindow()
    window.SetSize(500, 500)

    # Interactor offers some interaction functions for the user
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    # One can have several renderers per window
    renderer = vtk.vtkRenderer()
    window.AddRenderer(renderer)
    renderer.AddActor(actor)
    renderer.SetBackground(1.0, 1.0, 1.0)  # background color

    window.Render()
    interactor.Start()


if __name__ == '__main__':
    args = parser.parse_args()
    main(cgm_path=args.cgm, lgi_path=args.lgi)
