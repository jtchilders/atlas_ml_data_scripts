#!/usr/bin/python

import sys
import numpy as np

d=np.fromfile(sys.argv[1],dtype=np.float32)
print len(d)
print np.nonzero(d)
#print d


nz=np.nonzero(d)[0]
print nz
print len(nz)
for i in range(1,len(nz)):
  print nz[i-1],nz[i],nz[i]-nz[i-1]
