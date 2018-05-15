import bpy
import glob
import os
import sys
 
# switch on nodes
scene = bpy.context.scene
scene.use_nodes = True
tree = scene.node_tree
links = tree.links

# clear default nodes
for n in tree.nodes:
	tree.nodes.remove(n)

# get the directory path from the bash script
argv = sys.argv
argv = argv[argv.index("--") + 1:]
directorylist = argv
directory = ''.join(str(e) for e in directorylist)
tmpdir1 = directory+"/*.png"

# get the image directory
png_list = sorted(glob.glob(tmpdir1))

# create input image node
imageNode = tree.nodes.new('CompositorNodeImage')

# create output file node
fileOpNode = tree.nodes.new('CompositorNodeOutputFile')
fileOpNode.base_path = "/misc/lmbraid19/mayern/bharadwk/BLENDER_OUTPUT/TRAIN/A/0500/converted/"
fileOpNode.format.file_format= 'PNG'

# initialize exposure value
exposure_time = -5

for PNGs in png_list:
    image = bpy.ops.image.open(filepath=PNGs)    
    pngimg = PNGs.split('/')[10]
    imageNode.image = bpy.data.images[pngimg]
    imageNode.name = pngimg
    img = pngimg.split('.')[0]
    
    # Set camera exposure time	
    scene.view_settings.exposure = exposure_time
    
    fileOpNode.file_slots[0].path = img
    
    # create the links
    links.new(imageNode.outputs[0], fileOpNode.inputs[0])
    
    # empty render for saving the PNG files
    bpy.ops.render.render( write_still=True )
    
    # increment exposure by 1 in every iteration
    exposure_time = exposure_time + 1

# replace the PNGs with PNG
#cmd = "rm %s/*.png" %(directory)
#os.popen(cmd)

tmpdir2 = directory+"/*.png"

# rename the PNG images to the appropriate names
PNG_list = sorted(glob.glob(tmpdir2))

for PNGs in PNG_list:    
    pngimg = PNGs.split('/')[10]
    orgimg = pngimg
    img,img_format = pngimg.split('.')
    img = img.replace('0001','')
    orgimg = directory + '/' + orgimg
    finimg = img+'.'+img_format
    finimg = directory + '/' + finimg
    os.rename(orgimg, finimg)
