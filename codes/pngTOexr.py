import bpy
import glob
import os
import sys

#get respected file names
argv = sys.argv
file_name = argv[argv.index("--") + 1:]
file_name = file_name[0]

# switch on nodes
scene = bpy.context.scene
scene.use_nodes = True
tree = scene.node_tree
links = tree.links

# clear default nodes
for n in tree.nodes:
	tree.nodes.remove(n)

# get the image directory
PNG_list = sorted(glob.glob("/misc/lmbraid18/bharadwk/dataLDR/%s/*.JPG" %(file_name)))

# create input image node
imageNode = tree.nodes.new('CompositorNodeImage')

# create output file node
fileOpNode = tree.nodes.new('CompositorNodeOutputFile')
fileOpNode.base_path = "/misc/lmbraid18/bharadwk/dataLDR/%s" %(file_name)
fileOpNode.format.file_format= 'OPEN_EXR'

for PNGs in PNG_list:    
    
    image = bpy.ops.image.open(filepath=PNGs)    
    pngimg = PNGs.split('/')[6]
    imageNode.image = bpy.data.images[pngimg]
    imageNode.name = pngimg
    img = pngimg.split('.')[0]
    
    fileOpNode.file_slots[0].path = img
    
    # create the links
    links.new(imageNode.outputs[0], fileOpNode.inputs[0])
    
    # empty render for saving the PNG files
    bpy.ops.render.render( write_still=True )

