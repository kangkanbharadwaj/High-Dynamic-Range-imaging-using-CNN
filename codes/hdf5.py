import glob
import numpy as np
import cv2
import h5py
import os
import re

def keyFunc(afilename):
    nondigits = re.compile("\D")
    return int(nondigits.sub("", afilename))
    

ldr_files = glob.glob('/misc/lmbraid18/bharadwk/LDR_render_files/*')
hdr_files =  glob.glob('/misc/lmbraid18/bharadwk/hdr_rendered_image/*')

for items1 in ldr_files:
    for items2 in hdr_files:
        
        ldr_img = items1.split('/')[5]
        hdr_img = items2.split('/')[5]

        if ldr_img == hdr_img:

            files = glob.glob ("/misc/lmbraid18/bharadwk/LDR_render_files/%s/*.png" %(ldr_img)) 
            X_data1 = []
            arr_list = []

            for myFile in sorted(files, key=keyFunc):

                image = cv2.imread (myFile)
                X_data1.append (image)

            X_data2 = np.array(np.dstack(X_data1), dtype=np.float32)
            X_data2 = np.swapaxes(X_data2, 0, 2)
            X_data2 = np.swapaxes(X_data2, 1, 2)
            arr_list.append(X_data2)
            im_array = np.array(arr_list)            

            hdr_list = []            
            hdr_path = '/misc/lmbraid18/bharadwk/hdr_rendered_image/%s/hdr_image.exr' %(hdr_img)            
            hdr_image = cv2.imread(hdr_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)                        
            hdr_list.append(hdr_image)
            hdr_array = np.array(hdr_list, dtype=np.float32)
            hdr_array = np.swapaxes(hdr_array, 2, 3)
            hdr_array = np.swapaxes(hdr_array, 1, 2)

            with h5py.File('/misc/lmbraid18/bharadwk/workspace/ws1/training_data/%s.h5' %(hdr_img)) as hdf:

                D1 = hdf.create_dataset('data', data = im_array)
                D2 = hdf.create_dataset('hdr', data = hdr_array)