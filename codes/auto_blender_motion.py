import bpy
import mathutils
import sys
import os

#get respected file names
argv = sys.argv
file_name = argv[argv.index("--") + 1:]
file_name = file_name[0]
obj_list = []

#scene = bpy.data.scenes["Scene"].name
scene = bpy.context.scene
#scene.render.engine = 'CYCLES'
#scene.cycles.samples = 1000

scene.render.image_settings.color_mode = 'RGBA'
scene.render.alpha_mode = 'TRANSPARENT'

#scene.render.layers["RenderLayer"].use_pass_combined = False
#scene.render.layers["RenderLayer"].use_pass_z = False
scene.render.layers["RenderLayer"].use_pass_vector = True

# get the object
obj = bpy.data.objects["kangkan"]

# store the current location
loc = obj.location
tmp_loc = loc

#bpy.ops.wm.save_as_mainfile(filepath="/misc/lmbraid18/bharadwk/blend_motion/sledge43_new.blend")

exposure_time = -5
count = 0
init_loc = 0.1

#make the respective directories
cmd = 'mkdir /misc/lmbraid18/bharadwk/test_hdr_rendered_image_motion/%s' %(file_name)
os.popen(cmd)

#make the respective directories
cmd = 'mkdir /misc/lmbraid18/bharadwk/test_LDR_render_files_motion/%s' %(file_name)
os.popen(cmd)

while exposure_time <= 4:

	# adjustment values
	(x,y,z) = (0.0,init_loc,0.0)

	# adding adjustment values to the property
	obj.location = loc + mathutils.Vector((x,y,z))

	#increment the count by 1
	count = count + 1
	
	if exposure_time == 0:
		
		#Set render resolution
		scene.render.resolution_x = 640
		scene.render.resolution_y = 480
		scene.render.resolution_percentage = 100		
		
		#get the hdr resolution image for the scene
		scene.render.image_settings.file_format = 'OPEN_EXR'
		scene.render.image_settings.color_depth = '32'
		scene.render.filepath = '/misc/lmbraid18/bharadwk/test_hdr_rendered_image_motion/%s/hdr_image' %(file_name)
		bpy.ops.render.render( write_still=True )	

	# Set camera exposure time	
	scene.view_settings.exposure = exposure_time

	# Set render resolution
	scene.render.resolution_x = 640
	scene.render.resolution_y = 480
	scene.render.resolution_percentage = 100
	
	# Set Scenes camera and output filename 
	scene.render.image_settings.file_format = 'TIFF'
	scene.render.image_settings.color_depth = '16'
	scene.render.filepath = '/misc/lmbraid18/bharadwk/test_LDR_render_files_motion/%s/image_%d' %(file_name, count)

	# Render Scene and store the scene 
	bpy.ops.render.render( write_still=True )

	exposure_time = exposure_time + 1
	init_loc = init_loc + 0.01
