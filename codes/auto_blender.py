import bpy
import sys
import os

#get respected file names
argv = sys.argv
file_name = argv[argv.index("--") + 1:]
file_name = file_name[0]

#scene = bpy.data.scenes["Scene"].name
scene = bpy.context.scene
#scene.render.engine = 'CYCLES'
scene.cycles.samples = 500

#make the respective directories
cmd = 'mkdir /misc/lmbraid18/bharadwk/tmp1/%s' %(file_name)
os.popen(cmd)

# Set render resolution
scene.render.resolution_x = 640
scene.render.resolution_y = 480
scene.render.resolution_percentage = 100

#get the hdr resolution image for the scene
scene.render.image_settings.file_format = 'OPEN_EXR'
#scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
#scene.render.image_settings.file_format = 'HDR'
#scene.render.image_settings.color_mode = 'RGB'
#scene.render.alpha_mode = 'TRANSPARENT'
scene.render.filepath = '/misc/lmbraid18/bharadwk/tmp1/%s/hdr_image' %(file_name)
bpy.ops.render.render( write_still=True )

exposure_time = 0
count = 0

scene.render.use_motion_blur = True

#make the respective directories
cmd = 'mkdir /misc/lmbraid18/bharadwk/tmp2/%s' %(file_name)
os.popen(cmd)

while exposure_time <= 10:	
	
	#increment the count by 1
	count = count + 1
	
	# Set camera exposure time	
	#scene.view_settings.exposure = exposure_time
	#scene.cycles.film_exposure = exposure_time
	scene.render.motion_blur_shutter = exposure_time

	# Set render resolution
	scene.render.resolution_x = 640
	scene.render.resolution_y = 480
	scene.render.resolution_percentage = 100
	
	# Set Scenes camera and output filename 
	scene.render.image_settings.file_format = 'PNG'
	scene.render.filepath = '/misc/lmbraid18/bharadwk/tmp2/%s/image_%d' %(file_name, count)

	# Render Scene and store the scene 
	bpy.ops.render.render( write_still=True )

	exposure_time = exposure_time + 1
