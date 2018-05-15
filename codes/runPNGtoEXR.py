import os
import glob

file_list = []
file_list = glob.glob('/misc/lmbraid18/bharadwk/test_hdr_rendered_image/*')

for items in file_list:	
	file_name = items.split('/')[5]		
	cmd = '/misc/lmbraid18/bharadwk/blender/blender --background -noaudio --python EXR2PNG_short.py -- %s' %(file_name)
	os.popen(cmd)
