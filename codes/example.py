import sys
import glob
print sys.argv[0] # prints python_script.py
print sys.argv[1] # prints var1
print sys.argv[2] # prints var2
path = sys.argv[1]
path = ''.join(path)
print ("the apth is %s" %(path))


