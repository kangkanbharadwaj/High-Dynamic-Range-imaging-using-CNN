import cv2
import glob
import numpy as np

hdr_files =  glob.glob('/misc/lmbraid18/bharadwk/hdr_rendered_image/*')
fo = open('/misc/lmbraid18/bharadwk/workspace/min_max.txt','a')
fo.write("image name \t min value \t max value")

for paths in hdr_files:
    xpaths = paths
    hdr_img = xpaths.split('/')[5]
    hdr_path = paths+'/hdr_image.exr'    
    hdr_image = cv2.imread(hdr_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    hdr_arr = np.array(hdr_image)    
    fo.write(str(hdr_img))
    fo.write('\t')
    fo.write(str(hdr_arr.min()))
    fo.write('\t')
    fo.write(str(hdr_arr.max()))
    fo.write('\n')
fo.close()
