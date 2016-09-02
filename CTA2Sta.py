#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
'''Simple
@author: Li Jiapeng <distance4lee@gmail.com>
@license: LGPLv3+
'''

import os
import sys
from datetime import datetime,timedelta
import numpy as np
import struct
from scipy.interpolate import interp2d

def GetBinFname( dtinit ):
	DATADIR = '/media/cmacast/SATE_FY2E_L2L3/CTA/PUB'
	fn = 'Z_SATE_C_BAWX_*_P_FY2E_CTA_MLT_OTG_%s_%s15.AWX' % ( dtinit.strftime('%Y%m%d'), dtinit.strftime('%H') )
	fn_fullpath = os.popen('ls %s' % os.path.join(DATADIR, fn)).read()
	fn_fullpath = fn_fullpath.replace('\n','')
	print fn_fullpath
	return fn_fullpath

def DataLoader( dtinit ):
	fname = GetBinFname( dtinit )
	f = open( fname, 'rb')
	f.seek(2402)
	s = f.read(1201*1201)
	data = np.fromstring( s, 'B' ).reshape(1201,1201)
	f.close()
	return data

def Grid2Sta( dtinit ):

	stinfo = np.loadtxt('/home/enso/runtime/StaTcc/citycoord.dat')
	citycode = stinfo[:,0].reshape(len(stinfo),1)
	pts = stinfo[:,1:3]
	
	lat = np.arange(-60,60.1,0.1)[::-1]
	lon = np.arange(27,147.1,0.1)
	try:
		tccdata=[]
		data = DataLoader( dtinit )
		interp_f = interp2d( lon, lat, data )

		for pt in pts:
			tccdata.append(round(interp_f( pt[0], pt[1] ),1))

		tccdata = np.array(tccdata).reshape(len(pts),1)
		tccdata = np.hstack((citycode,tccdata))
	except:
		tccdata = np.ones(len(pts)).reshape(len(pts),1) * -999.0
		tccdata = np.hstack((citycode,tccdata))
	return tccdata

if __name__=="__main__":

	try:
		dtstr = os.popen("date -d '-9 hours' +%Y%m%d%H").read()
		dtstr = dtstr.replace('\n','')
		#dtstr = '2016041104'
	except:
		exit()

	dtinit = datetime.strptime( dtstr, '%Y%m%d%H' )

	print dtinit

	tcc = Grid2Sta( dtinit )

	#fout = 'FY2E_CTA_%s30_UTC.dat' % ( dtinit.strftime('%Y%m%d%H') )
	TMPDIR = '/home/enso/runtime/StaTcc/tmp'
	OUTDIR = '/data/StaTcc/%s' % ( dtinit.strftime('%Y%m') )
	os.system('mkdir -p %s' % (OUTDIR))
	fout = 'FY2E_CTA_%s15_UTC.dat' % ( dtinit.strftime('%Y%m%d%H') )
	fn_fullpath =  os.path.join(TMPDIR, fout)
	print fn_fullpath

	np.savetxt(fn_fullpath,tcc,fmt='%8i%8.1f')

	os.system('mv -u %s %s' % (fn_fullpath,OUTDIR))


	
