import os
import glob

file_list = []
file_list = glob.glob('/misc/lmbraid18/bharadwk/blend/*.blend')

for items in file_list:	
	file_name = items.split('/')[5]
	file_name = file_name.split('.')[0]
	#cmd = '/misc/lmbraid18/bharadwk/blender/blender --background -noaudio %s --python auto_blender_motion.py -- %s' %(items,file_name)
	cmd = '/misc/lmbraid19/mayern/bharadwk/blender-bin/blender --background -noaudio %s --python auto_blender.py -- %s' %(items,file_name)
	os.popen(cmd)
	
	
