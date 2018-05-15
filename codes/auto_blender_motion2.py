import os
import sys
import bpy
import mathutils
import random
from math import radians
from mathutils import Euler

#get respected file names
argv = sys.argv
file_name = argv[argv.index("--") + 1:]
file_name = file_name[0]
obj_list = []

#scene = bpy.data.scenes["Scene"].name
scene = bpy.context.scene
#scene.render.engine = 'CYCLES'
scene.cycles.samples = 200

# get the object
obj = bpy.data.objects["kangkan"]
#obj2 = bpy.data.objects["kangkan2"]

# store the current location
loc = obj.location
angle = obj.rotation_euler
tmp_loc = loc

#bpy.ops.wm.save_as_mainfile(filepath="/misc/lmbraid18/bharadwk/blend_motion/sledge43_new.blend")

exposure_time = -5
count = 0
init_x = 0.1
init_y = 0.1
init_z = 0.1
rot_x = 0.0
rot_y = 0.0
rot_z = 0.0

#make the respective directories
cmd = 'mkdir /misc/lmbraid18/bharadwk/test_hdr_rendered_image_trans_rot/%s' %(file_name)
os.popen(cmd)

#make the respective directories
cmd = 'mkdir /misc/lmbraid18/bharadwk/test_LDR_render_files_trans_rot/%s' %(file_name)
os.popen(cmd)

while exposure_time <= 4:

	# adjustment values
	rand_choice = random.choice([init_x, init_y, init_z])		
	
	if rand_choice == init_x:
		(x,y,z) = (init_x,0.0,0.0)		
		init_x = init_x + random.random()
	elif rand_choice == init_y:
		(x,y,z) = (0.0,init_y,0.0)		
		init_y = init_y + random.random()
	else:
		(x,y,z) = (0.0,0.0,init_z)		
		init_z = init_z + random.random()	

	# adding adjustment values to the property
	obj.location = loc + mathutils.Vector((x,y,z))	
	obj.rotation_euler = Euler((rot_x, rot_y, rot_z), 'XYZ')

	#increment the count by 1
	count = count + 1
	
	if exposure_time == 0:
		
		#Set render resolution
		scene.render.resolution_x = 640
		scene.render.resolution_y = 480
		scene.render.resolution_percentage = 100
		
		#get the hdr resolution image for the scene
		scene.render.image_settings.file_format = 'OPEN_EXR'
		scene.render.filepath = '/misc/lmbraid18/bharadwk/test_hdr_rendered_image_trans_rot/%s/hdr_image' %(file_name)
		bpy.ops.render.render( write_still=True )	

	# Set camera exposure time	
	scene.view_settings.exposure = exposure_time

	# Set render resolution
	scene.render.resolution_x = 640
	scene.render.resolution_y = 480
	scene.render.resolution_percentage = 100
	
	# Set Scenes camera and output filename 
	scene.render.image_settings.file_format = 'PNG'
	scene.render.filepath = '/misc/lmbraid18/bharadwk/test_LDR_render_files_trans_rot/%s/image_%d' %(file_name, count)

	# Render Scene and store the scene 
	bpy.ops.render.render( write_still=True )

	exposure_time = exposure_time + 1
	rot_x = rot_x + 5.0
	rot_y = rot_y + 5.0
	rot_z = rot_z + 5.0
