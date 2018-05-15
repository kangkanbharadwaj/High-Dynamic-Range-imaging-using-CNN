import PIL
from PIL import Image
import glob
import subprocess as sp

dir_list = []
dir_list = glob.glob('/misc/lmbraid18/bharadwk/data/data*')

for paths in dir_list:
    
    subfolder = paths.split('/')[5]    
    #cmd = 'mkdir /misc/lmbraid18/bharadwk/scaled_data/%s' %(subfolder)
    #sp.Popen(cmd, shell=True)
    #print(subfolder)
    #paths = paths+'*.png'    
    img_list = glob.glob("%s/*.png" %(paths))    
    new_img_list = []
    tmp_list = []

    for i in range(0,len(img_list)): 
        img_name = ''
        ximg_name = ''
        count = 0
        for j in range(0, len(img_list)):
            
            img_name = img_list[i].split('/')[6]            
            ximg_name = img_list[j].split('/')[6]
            
            if 'cc' in img_name:
                img_name = img_name.split('_')[0]
                img_name = img_name + '_CC'
            else:
                img_name = img_name.split('_')[0]
            
            if 'cc' in ximg_name:
                ximg_name = ximg_name.split('_')[0]
                ximg_name = ximg_name + '_CC'
            else:
                ximg_name = ximg_name.split('_')[0]            
            
            if img_name == ximg_name and ximg_name not in tmp_list:
                
                count = count + 1                
                image_name = ximg_name + '_' + str(count)
                new_img_list.append(image_name)
                
                #Resizing width:
                new_width  = 2080
                
                #Resizing height:
                new_height = 1408
                
                img = Image.open(img_list[j])
                #img = img.resize((new_width, new_height), Image.ANTIALIAS) 
                img.save('/misc/lmbraid18/bharadwk/scaled_data_ldr/%s/%s.png' %(ximg_name,image_name))
        
        tmp_list.append(img_name)