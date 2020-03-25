#!/usr/bin/env python

import os

for i in range(1,11):
	for j in range(1,11):
		os.system("wget --retry-connrefused --tries=20 -c https://s3.cern.ch/swift/v1/gan-bucket/EleEscan_EleEscan_%s_%s.h5.h5 &" % (i,j))
		#actually fails: downloads 66 instead of 68 files and only half of each file
