#!/bin/bash

export LD_LIBRARY_PATH=/misc/student/mayern/Blender/OpenImageIO/install/lib:$LD_LIBRARY_PATH;
export LD_LIBRARY_PATH=/misc/student/mayern/Blender/OpenEXR/install/lib:$LD_LIBRARY_PATH;
export LD_LIBRARY_PATH=/misc/student/mayern/Blender/OpenCOLLADA/install/lib/opencollada:$LD_LIBRARY_PATH;
export LD_LIBRARY_PATH=/misc/student/mayern/OpenNI-Bin-Dev-Linux-x64-v1.5.4.0/Lib:$LD_LIBRARY_PATH;

cd /misc/lmbraid18/bharadwk/py_files/
python run_blender.py
