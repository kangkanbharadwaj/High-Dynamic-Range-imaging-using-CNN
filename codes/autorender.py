#
# scriptfile='/home/ummenhof/projects/autoscenerender/scripts/autorender.py'; exec(compile(open(scriptfile).read(), scriptfile, 'exec'))
#
# import sys; sys.path.append('/home/ummenhof/projects/autoscenerender/scripts/'); import autorender
#
import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix
import math
import random
import itertools
from glob import glob
import os
import sys
import tempfile
import argparse
import time
import numpy as np
import json
import re

LOOKAT_NOISE = 0.1 # relative to the distance between camera and lookat
ANGLE_THRESHOLD = math.cos(45*math.pi/180)
DISTANCE_THRESHOLD_FACTOR = 0.7 # allowed change in the distance to the lookat
OPTICAL_AXIS_ROTATION_SIGMA = 4*math.pi/180

# intrinsics as in sun3d
IMG_SIZE = [640, 480]
FOCAL_LENGTH = 28.5 # mm

# global scene shortcut
_scene = bpy.context.scene

# command line parameters
_args = None


#
# small helper functions
#
def bounding_box_world(obj):
    """ Returns (xmin,ymin,zmin,xmax,ymax,zmax) in world coordinates """
    xmin = float('inf')
    ymin = float('inf')
    zmin = float('inf')
    xmax = -float('inf')
    ymax = -float('inf')
    zmax = -float('inf')
    bb = obj.bound_box
    M = obj.matrix_world
    for p in bb:
        pw = M*Vector(p[:])
        xmin = min(pw[0],xmin)
        ymin = min(pw[1],ymin)
        zmin = min(pw[2],zmin)
        xmax = max(pw[0],xmax)
        ymax = max(pw[1],ymax)
        zmax = max(pw[2],zmax)
    return xmin,ymin,zmin,xmax,ymax,zmax


def is_point_in_bounding_box(world_bb, point):
    """ 
    Tests if the point is inside the bounding box. 
    The bounding box is a 6-tuple.
    """
    xmin,ymin,zmin,xmax,ymax,zmax = world_bb
    if point[0] < xmin or point[0] > xmax:
        return False
    if point[1] < ymin or point[1] > ymax:
        return False
    if point[2] < zmin or point[2] > zmax:
        return False
    return True


def bounding_box_edge_lengths(obj):
    """ Returns the bounding box edge lengths in world units """
    xmin,ymin,zmin,xmax,ymax,zmax = bounding_box_world(obj)
    x_length = xmax-xmin
    y_length = ymax-ymin
    z_length = zmax-zmin
    return x_length, y_length, z_length   


def bounding_box_volume(obj):
    """ Returns the bounding box volume in world units """
    x_length, y_length, z_length = bounding_box_edge_lengths(obj)
    return x_length*y_length*z_length
    

def random_unit_vec():
    v = Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-1,1)))
    while v.length_squared < 1e-6:
        v = Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-1,1)))
    return v.normalized()


def add_noise_to_pos_uniform(pos, noise_strength):
    s = 0.5*noise_strength
    return pos[0]+random.uniform(-s,s), pos[1]+random.uniform(-s,s), pos[2]+random.uniform(-s,s)
    

def random_discrete_dist(weights):
    total = sum(weights)
    selected = random.random()*total
    for i in range(len(weights)):
        selected -= weights[i]
        if selected < 0:
            return i
    return len(weights)-1

    
def random_point_in_volumes(volumes):
    """ Returns a random point in the space described by the volumes """
    objects = [obj for obj,vol in volumes]
    vols = [vol for obj,vol in volumes]
    obj = objects[random_discrete_dist(vols)]

    xmin,ymin,zmin,xmax,ymax,zmax = bounding_box_world(obj)
    x = random.uniform(xmin,xmax)
    y = random.uniform(ymin,ymax)
    z = random.uniform(zmin,zmax)
    return x, y, z


def random_point_in_volume_groups(volume_groups):
    """ Returns a random point and the key for the randomly selected volume group """
    keys = []
    weights = []
    for key,value in volume_groups.items():
        keys.append(key)
        vols = [vol for obj,vol in value]
        weights.append(sum(vols))
        
    key = keys[random_discrete_dist(weights)]
    x,y,z = random_point_in_volumes(volume_groups[key])
    return (x,y,z), key
    

def is_point_in_volumes(volumes, point):
    """ Returns true if the point is in one of the volumes """
    for vol in volumes:
        bb = bounding_box_world(vol[0])
        if is_point_in_bounding_box(bb,point):
            return True
    return False

    
def is_point_in_volume_groups(volume_groups, point):
    """ Returns true if the point is in one of the volumes """
    for key,volume in volume_groups.items():
        if is_point_in_volumes(volume,point):
            return True
    return False
    

def look_at(obj,target_point):
    """ Makes the obj look at the target_point """
    direction = target_point-obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    # use euler ZYX to make it easy to rotate the camera around the optical axis
    obj.rotation_mode = 'ZYX'
    obj.rotation_euler = rot_quat.to_euler('ZYX')
    


class SceneInfos:
    """ 
    Class that holds information about the scene and some shortcuts
    """
    def __init__(self):
        self.blend_filename = os.path.basename(bpy.data.filepath)
        self.original_active_camera = _scene.camera
        self.original_frame_start = _scene.frame_start
        self.original_frame_end = _scene.frame_end
        # count the number of active render layers            
        active_render_layers_count = 0
        for render_layer in _scene.render.layers:
            if render_layer.use:
                active_render_layers_count += 1
        
        if active_render_layers_count != 1:
            raise Exception("There must be exactly one active render layer! ("+str(active_render_layers_count))

        # get the first active render layer
        for render_layer in _scene.render.layers:
            if render_layer.use:
                self.render_layer = render_layer
                break
        
        # try to find the special objects that define the scale and hide them
        # for rendering
        self.scale = 1 # this should be roughly one meter in blender units
        if "__HUMAN" in bpy.data.objects:
            human = bpy.data.objects["__HUMAN"]
            human.hide_render = True
            self.scale = max(bounding_box_edge_lengths(human))/1.80
            

        #
        # collect the annotated volumes
        #
        rx_cam = re.compile(r'__CAM(\w?)(\.\d*)?')
        rx_look = re.compile(r'__LOOK(\w?)(\.\d*)?')
        rx_dontlook = re.compile(r'__DONTLOOK(\w?)(\.\d*)?')
        # examples: '__CAMa.002'
        # __CAM means camera volume 
        # 'a' is the group for the volume
        # '.002' is the suffix appended by blender by duplicating

        self.camera_volume_groups = {}
        self.look_volume_groups = {}
        self.dontlook_volume_groups = {}

        pairs = [
            [rx_cam,self.camera_volume_groups],
            [rx_look,self.look_volume_groups],
            [rx_dontlook,self.dontlook_volume_groups]
        ]
        
        for obj in bpy.data.objects:
            for rx, volume_group in pairs:
                match = rx.match(obj.name)
                if match:
                    key = match.group(1)
                    if not key in volume_group:
                        volume_group[key] = []
                    volume_group[key].append((obj, bounding_box_volume(obj)))

        if __name__ == '__main__':
            if not self.camera_volume_groups:
                raise Exception("no camera volumes found")
            if not self.look_volume_groups:
                raise Exception("no lookat volumes found")
        



def get_camera_parameters(cam,scene):
    """ Returns the camera parameters as K,R,t """
    w = scene.render.resolution_x*scene.render.resolution_percentage/100.0
    h = scene.render.resolution_y*scene.render.resolution_percentage/100.0
    focal_length = w/2.0 / math.tan(cam.data.angle/2)
    M = cam.matrix_world.inverted()
    t = M.to_translation()
    R = M.to_3x3()
    K = Matrix.Identity(3)
    K[0][0] = focal_length
    K[1][1] = focal_length
    K[0][2] = w/2.0;
    K[1][2] = h/2.0;
        
    # blender uses a right handed coordinate system with the camera pointing
    # in -z direction.
    # we want a right handed system with the camera pointing in +z such that 
    # the pixel coordinates correpond to the usual image coordinates 
    # (x axis pointing right, y axis pointing down, origin in the top left corner)
    #
    # -> append transformation inverting y and z (180deg rotation around x)
    convert_mat = Matrix.Identity(3)
    convert_mat[1][1] = -1
    convert_mat[2][2] = -1
    R = convert_mat*R
    t = convert_mat*t

    return { 'K': K, 'R': R, 't':t }


def get_current_frame_output_path(outfile_node, output):
    """ Returns the path that will be generated for this output """
    file_extensions = {'PNG': '.png', 'JPEG': '.jpg', 'PFM': '.pfm', 'OPEN_EXR': '.exr'}
    
    slot = outfile_node.file_slots[output]
    filename = outfile_node.base_path
    filename = os.path.join(filename, slot.path)
    filename += str(_scene.frame_current).zfill(4)
    if slot.use_node_format:
        filename += file_extensions[outfile_node.format.file_format]
    else:
        filename += file_extensions[slot.format.file_format]
        
    return os.path.normpath(filename)
    

def is_object_visible_in_camera_approx(obj,cam):
    """ 
        Quickly checks if the obj is visible by raycasting (20 rays).
        This is just a quick visiblity check and is not pixel precise.
        'False' means 'maybe' and 'True' means 'True'.

        Make sure to call update() on the current scene before using this function
    """
    # rows*cols == number of rays
    rows = 4
    cols = 5


    #    frame
    #  3--------0
    #  |        |
    #  |        |
    #  2--------1
    frame = cam.data.view_frame(_scene)
    frame = [cam.matrix_world * v for v in frame]
    frame_x_vec = (frame[0] - frame[3])/cols
    frame_y_vec = (frame[2] - frame[3])/rows


    world_to_obj = obj.matrix_world.inverted()    

    origin = cam.location
    origin_local = world_to_obj*origin
    for y in range(rows):
        for x in range(cols):
            p = frame[3] + frame_x_vec*(x+0.5) + frame_y_vec*(y+0.5)
            p_local = world_to_obj*p
            ray_dir = (p_local-origin_local).normalized()
            intersection, _, _, _ = obj.ray_cast(origin_local,ray_dir)
            #bpy.ops.mesh.primitive_cube_add(location=p)
            #bla = bpy.context.object
            #s = 0.001
            #bla.scale = Vector((s,s,s))
            if intersection:
                return True

    return False # maybe


def hide_special_objects():
    """ Hide all objects that start with '__' """
    for obj in bpy.data.objects:
        if obj.name.startswith('__'):
            obj.hide_render = True
            if obj.name.startswith('__LOOK') or obj.name.startswith('__CAM'):
                obj.draw_type = 'BOUNDS'


def setup_renderer():
    if _scene.render.engine == 'CYCLES':
        setup_renderer_cycles()
    elif _scene.render.engine == 'BLENDER_RENDER':
        setup_renderer_blender()
    else:
        raise Exception("unsupported render engine")

    if _args.threads:
        _scene.render.threads_mode = 'FIXED'
        _scene.render.threads = _args.threads
    else:
        _scene.render.threads_mode = 'AUTO'

    _scene.render.resolution_x = IMG_SIZE[0]
    _scene.render.resolution_y = IMG_SIZE[1]
    _scene.render.resolution_percentage = 100

    _scene.render.tile_x = 64
    _scene.render.tile_y = 48

    # write output to a tmp dir
    _scene.render.filepath = '/tmp/blendertmprender'

    # dont render stamp metadata
    _scene.render.use_stamp = False

    # deactivate border
    _scene.render.use_border = False

    
def setup_renderer_cycles():
    _scene.cycles.device = 'CPU'
    _scene.cycles.use_progressive_refine = False
    # TODO limit number of samples ?

def setup_renderer_blender():
    pass


def add_camera(pos, lookat_pos, volume_group_key = None, preview_cam = None):
    if not preview_cam:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
    else:
        cam = preview_cam

    # copy some parameters from the original active camera
    cam.data.clip_start = _sceneinfos.original_active_camera.data.clip_start
    cam.data.clip_end = _sceneinfos.original_active_camera.data.clip_end

    # intrinsic parameters
    cam.data.lens = FOCAL_LENGTH # mm
    cam.data.sensor_width = 32.0
    
    # extrinsic parameters
    # add noise to the positions
    distance = (lookat_pos-pos).length
    view_dir = (lookat_pos-pos).normalized()
    
    cam_lookat_pos = add_noise_to_pos_uniform(lookat_pos,distance*LOOKAT_NOISE)
    
    key = volume_group_key
    success = False
    iteration = 0
    while not success and iteration < 100:
        iteration += 1
        print(iteration)

        if key in _sceneinfos.camera_volume_groups:
            cam_pos = random_point_in_volumes(_sceneinfos.camera_volume_groups[key])
        else:
            cam_pos, _ = random_point_in_volume_groups(_sceneinfos.camera_volume_groups)
        cam_pos = Vector(cam_pos)

        # test the angle between view_dir and cam_view_dir
        cam_view_dir = (lookat_pos-cam_pos).normalized()
        dot = view_dir.dot(cam_view_dir)
        if dot < ANGLE_THRESHOLD:
            continue
    
        # test the distance to the lookat
        cam_distance = (lookat_pos-cam_pos).length
        factor = min(distance,cam_distance)/max(distance,cam_distance)
        if factor < DISTANCE_THRESHOLD_FACTOR:
            continue

        
        # check if the camera sees some of the dontlook volumes
        cam.location = cam_pos
        look_at(cam,Vector(cam_lookat_pos))

        # rotate the camera a little around the optical axis
        cam.rotation_euler.z += random.gauss(0, OPTICAL_AXIS_ROTATION_SIGMA)
        

        _scene.update() # scene update is required before call to is_object_visible_in_camera_approx()
        dontlook_visible = False
        if _sceneinfos.dontlook_volume_groups:
            for k,v in _sceneinfos.dontlook_volume_groups.items():
                if dontlook_visible:
                    break
                for dontlook in v:
                    if is_object_visible_in_camera_approx(dontlook[0],cam):
                        dontlook_visible = True
                        break
        if dontlook_visible:
            continue
            

        success = True # all tests passed

        
    if not success:
        if not preview_cam:
            cam.select = True
            bpy.ops.object.delete()
        return None
        

    if not preview_cam:
        # go to a new frame
        _scene.frame_current = _scene.frame_end + 1
        _scene.frame_end += 1

        # bind camera to new marker
        marker = _scene.timeline_markers.new("F_{0}".format(_scene.frame_current), _scene.frame_current)
        marker.camera = cam

    return cam

        

def setup_cameras(num_lookat, cams_per_lookat, preview_cam = None):

    camera_groups = []

    if not _sceneinfos.look_volume_groups or not _sceneinfos.camera_volume_groups:
        return
    
    for i in range(num_lookat):
        iteration = 0
        cam_group = []

        while len(cam_group) < min(3,cams_per_lookat) and iteration < 100:
            print('----'+str(iteration))
            cam_group = []
            lookat_pos, key = random_point_in_volume_groups(_sceneinfos.look_volume_groups)

            if key in _sceneinfos.camera_volume_groups:
                cam_pos = random_point_in_volumes(_sceneinfos.camera_volume_groups[key])
            else:
                cam_pos, _ = random_point_in_volume_groups(_sceneinfos.camera_volume_groups)

            for cam_i in range(cams_per_lookat):
                if add_camera(Vector(cam_pos), Vector(lookat_pos), key, preview_cam):
                    cam_group.append(_scene.frame_current)

            iteration += 1

        if len(cam_group) >= 3 or len(cam_group) == cams_per_lookat:
            camera_groups.append(cam_group)

    return camera_groups
    


# this operator is for previewing the generated camera poses
class PreviewCameraPose(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "view3d.preview_camera_pose"
    bl_label = "Generates a sample camera pose for the active camera"
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        cam = context.scene.camera

        global _sceneinfos
        _sceneinfos = SceneInfos()

        _scene.render.resolution_x = IMG_SIZE[0]
        _scene.render.resolution_y = IMG_SIZE[1]

        setup_cameras(1,1,cam)
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PreviewCameraPose)

def unregister():
    bpy.utils.unregister_class(PreviewCameraPose)



def setup_objectids():
    idx = 1
    for obj in _scene.objects:
        obj.pass_index = idx
        idx += 1


def setup_compositing_nodes():

    # make sure Z and object pass are enabled
    _sceneinfos.render_layer.use_pass_z = True
    _sceneinfos.render_layer.use_pass_object_index = True
        
    if _scene.use_nodes:
        pass # TODO analyze existing node graph or redo everything
        #raise Exception("scene already uses nodes")
    else:
        _scene.use_nodes = True
        
    node_tree = _scene.node_tree

    render_layer_node = None
    for node in node_tree.nodes:
        # use the first render layer node
        if node.type == 'R_LAYERS':
            render_layer_node = node
        # remove file output nodes
        elif node.type == 'OUTPUT_FILE':
            node_tree.nodes.remove(node)

    # create a new render layer node if there is no one
    if not render_layer_node:
        render_layer_node = node_tree.nodes.new('CompositorNodeRLayers')

    
    
    outfile_node = node_tree.nodes.new('CompositorNodeOutputFile')
    _sceneinfos.outfile_node = outfile_node
    outfile_node.base_path = _args.outputpath

    # image output
    outfile_node.format.file_format = 'PNG'
    outfile_node.file_slots[0].path = "image_"
    node_tree.links.new(render_layer_node.outputs['Image'], outfile_node.inputs[0])

    # object ids output
    # output for object ids
    math_node = node_tree.nodes.new('CompositorNodeMath')
    math_node.operation = 'DIVIDE'
    math_node.inputs[1].default_value = 2**16-1
    
    outfile_node.file_slots.new("objectids")
    slot = outfile_node.file_slots["objectids"]
    slot.path = "objectids_"
    slot.use_node_format = False
    slot.format.file_format = 'PNG'
    slot.format.color_mode = 'BW'
    slot.format.color_depth = '16'
    node_tree.links.new(render_layer_node.outputs['IndexOB'], math_node.inputs[0])
    node_tree.links.new(math_node.outputs[0], outfile_node.inputs["objectids"])

    # output for depth map
    outfile_node.file_slots.new("depth")
    slot = outfile_node.file_slots["depth"]
    slot.path = "depth_"
    slot.use_node_format = False
    slot.format.file_format = 'OPEN_EXR'
    slot.format.color_depth = '32'
    node_tree.links.new(render_layer_node.outputs['Z'], outfile_node.inputs["depth"])



def main():
    #
    # parse cmdline
    #
    print(sys.argv)

    argv = None
    try:
        argv = sys.argv[sys.argv.index("--")+1:] # remove the blender argv part
        print(argv)
    except:
        argv = []

    global _args
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--seed",type=int)
        parser.add_argument("--threads",type=int)
        parser.add_argument("--num_lookat",type=int,default=10)
        parser.add_argument("--num_cameras",type=int,default=4)
        parser.add_argument("--outputpath")
        parser.add_argument("--setname")
        parser.add_argument("--norender", action='store_true')
        _args = parser.parse_args(args=argv)
        print(_args)
    except:
        return

    if _args.seed is None:
        _args.seed = int(time.time()*1000) # time in milliseconds
        print("seed = ", _args.seed, "  generated from current time")
    random.seed(_args.seed)

    if _args.outputpath is None:
        _args.outputpath = "/tmp/"

    if not os.path.exists(_args.outputpath):
        os.makedirs(_args.outputpath)



    # assume we are always in object mode after this    
    bpy.ops.object.mode_set(mode='OBJECT')

    # init the global _sceneinfos object
    global _sceneinfos
    _sceneinfos = SceneInfos()

    if _args.setname is None:
        _args.setname = _sceneinfos.blend_filename.strip() 


    hide_special_objects()
    setup_renderer()
    setup_objectids()
    camera_groups = setup_cameras(_args.num_lookat,_args.num_cameras)
    setup_compositing_nodes()


    # render
    if not _args.norender:
        group_count = 0
        for cam_group in camera_groups:
            
            infovec = []
            json_filename = _args.setname+"_"+str(group_count)+".json"
            json_filename = os.path.join(_args.outputpath, json_filename)
            if not os.path.exists(json_filename):
                for frame in cam_group:
                    print("Creating frame ", frame)
                    _scene.frame_current = frame
                    _scene.update()
                    bpy.ops.render.render(animation=False)

                
                    # write file with additional information about the current frame
                    #(image_filename, objectids_filename, depth_filename) = get_current_frame_outpus_paths()
                    #print(image_filename)
                    camera_parameters = get_camera_parameters(_scene.camera,_scene) 
                    
                    info = {}
                    info['image'] = os.path.basename(get_current_frame_output_path(_sceneinfos.outfile_node,"image_"))
                    info['objectids'] = os.path.basename(get_current_frame_output_path(_sceneinfos.outfile_node,"objectids_"))
                    info['depth'] = os.path.basename(get_current_frame_output_path(_sceneinfos.outfile_node,"depth_"))
                    info['frame'] = frame
                    info['seed'] = _args.seed
                    info['group_name'] = _args.setname+"_"+str(group_count)
                    info['K'] = [camera_parameters['K'].col[0].to_tuple(),
                                 camera_parameters['K'].col[1].to_tuple(),
                                 camera_parameters['K'].col[2].to_tuple()]
                    info['R'] = [camera_parameters['R'].col[0].to_tuple(),
                                 camera_parameters['R'].col[1].to_tuple(),
                                 camera_parameters['R'].col[2].to_tuple()]
                    info['t'] = camera_parameters['t'].to_tuple()
                    info['matrix_storage'] = 'column-major'
                    info['renderer'] = bpy.context.scene.render.engine
                    #print(json.dumps(info))
                    infovec.append(info)

                with open(json_filename, 'w') as f:
                    json.dump(infovec, f, indent=2)
                    #json.dump(infovec, f)

            group_count += 1




if __name__ == '__main__':
    main()

