#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import vtk

def vtk2stl(fn_in, fn_out):

    reader = vtk.vtkDataSetReader()
    reader.SetFileName(fn_in)
    reader.Update()

    gfilter = vtk.vtkGeometryFilter()
    if vtk.VTK_MAJOR_VERSION <= 5:
        gfilter.SetInput(reader.GetOutput())
    else:
        gfilter.SetInputData(reader.GetOutput())
        gfilter.Update()

    writer = vtk.vtkSTLWriter()
    writer.SetFileName(fn_out)
    if vtk.VTK_MAJOR_VERSION <= 5:
        writer.SetInput(gfilter.GetOutput())
    else:
        writer.SetInputData(gfilter.GetOutput())
    writer.Write()

def main():
    fname, ext = os.path.splitext(sys.argv[1])
    vtk2stl('%s.vtk' % fname, '%s.stl' % fname)

if __name__ == "__main__":
    main()
