import glob

fo = open("/misc/lmbraid18/bharadwk/workspace/ws1/trainfilelist.txt", "w")
file_list = glob.glob("/misc/lmbraid18/bharadwk/workspace/ws1/training_data/*.h5")
l_o_list = len(file_list)
print l_o_list

for i in range (0,l_o_list):
	#print file_list[i]	
	fo.write(file_list[i])
	#if i != l_o_list - 1:
	fo.write('\n')
fo.close()
