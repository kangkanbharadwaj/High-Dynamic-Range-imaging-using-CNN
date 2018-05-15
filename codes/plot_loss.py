import glob
import matplotlib.pyplot as plt

log_list = []
loss_list = []
log_list = sorted(glob.glob('/misc/lmbraid18/bharadwk/workspace/ws1/*.log'))


for items in log_list:
	filename = items.split('/')[6]
	fo1 = open(items, 'r')
	filelist = fo1.readlines()	
	for pos, xitems in enumerate(filelist):				
		if 'Train net output' in xitems:
			loss = 0											
			loss = filelist[pos].split('=')[1]
			loss = loss.split('(')[0]
			loss_list.append(loss)
#print loss_list
plt.plot(loss_list)
plt.ylabel('l2 norm loss')
plt.show()
