import glob
import numpy as np
import collections

log_file = []
file_list = []
loss_list_mean = {}

log_file = sorted(glob.glob('/misc/lmbraid18/bharadwk/workspace/ws1/hdr_test_logs_HDRNorm/hdr_test_hdr_snapshot*.log'))

for logs in log_file:    
    fo = open(logs,"r")
    logs = logs.split('/')[7]
    logs = logs.split('_')[5]
    logs = logs.split('.')[0]
    file_list = fo.readlines()
    loss_list = []
    mean = 0.0
    
    for pos, xitems in enumerate(file_list):        
        if 'Successfully saved 1 blobs' in xitems:            
            
            pos = pos + 1
            tmp_str = file_list[pos]
            tmp_str = tmp_str.split('=')[1]
            loss_list.append(float(tmp_str))
        
    mean = np.mean(loss_list)    
    loss_list_mean.update({logs:mean})         

loss_list_mean = collections.OrderedDict(sorted(loss_list_mean.items(), key=lambda t: len(t[0])))

testlog = list(loss_list_mean.values())

for pos,loss in enumerate(testlog):
    for i in range(0,4999):
        testlog.insert(pos,0.0)
