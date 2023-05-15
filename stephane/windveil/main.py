
import numpy as np
import pylab as plt
import glob
import os
import socket
import platform
import mpmath as math
import cv2

#Scipy modules
import scipy.integrate as inte
import scipy.special as special
import scipy.interpolate as interp

#Personal modules
import stephane.display.graphes as graphes
import stephane.tools.Smath as smath
#import sympy #symoblic python

import stephane.windveil.facades as wind

#Global variables
global osname,ostype
ostype = platform.platform().split('-')[0]
osname = socket.gethostname()

def get_files(base,date,ext=None,prefix=''):
    serveurfolder = find_path(base)
    print(serveurfolder+date+'/'+prefix+'*.'+ext)
    filelist = glob.glob(serveurfolder+date+'/'+prefix+'*.'+ext)
    print(filelist)
    return filelist    

def find_path(base):
	print('OS type : '+str(osname))

	if 'Windows' in ostype:    
		serveurfolder = 'W:/'+base #fucking windows OS : beware of the mounting disk you used
    
	if 'Linux' in ostype:
		if 'thiou' in osname:
			serveurfolder = '/volume3/labshared2/'+base #praise UNIX system    		
		else:
			serveurfolder = '/media/turbots/DATA/thiou/labshared2/'+base #praise UNIX system
	if 'Darwin' in ostype:# or 'laita' in osname:    
		serveurfolder = '/Volumes/labshared2/'+base #praise UNIX system        

	return serveurfolder

def process_movie(imlist,title,savefolder):
    print(len(imlist))
    M = wind.read_images(imlist)
    
    F,Ky,TF_yt_moy = wind.compute_fft_xt(M)
    figs = wind.display_fft_xt(F,Ky,TF_yt)
    
    plt.show()
    print(toto)
    
    fig,ax = wind.display_image(M[...,0])
    figs = graphes.legende('X (pix)','Y (pix)',title,ax=ax)
    graphes.save_figs(figs,savedir=savefolder,prefix='im1_')    
    #plt.show()
    
    f,TF_t,f0,Imax = wind.compute_fft_t(M)
    figs = wind.display_fft(f,TF_t,f0,Imax,title)
    graphes.save_figs(figs,savedir=savefolder)    
    #plt.show()
    
    print(f0)
    figs = wind.display_filtered(M,f0)
    graphes.save_figs(figs,savedir=savefolder)    
    #plt.show()
    
    
    
    #t = time_axis(M)
    #Res = compute_rd(M,t)
    #figs = display_rd(Res)
    #graphes.save_figs(figs,savedir=savefolder)    
    
def main(folder=None):
    base = 'Windveil/NedFacades/recaps/ImgsDewarp/'
    basefolder = find_path(base)
    folders = glob.glob(basefolder+'h*/scene*/zone*')
    print(len(folders))

    for folder in folders[30:]:
        bfolder = os.path.dirname(folder)
        name = os.path.basename(folder)
        savefolder = bfolder+'/Results_'+name+'/'
        if not os.path.isdir(savefolder):
            os.makedirs(savefolder)
            
        imlist = glob.glob(folder+'/*.tif')
        print(folder,len(imlist),savefolder)
        title = str(folder.split('/')[-3:])
        if len(imlist)>0:
            process_movie(imlist,title,savefolder)
                
if __name__=='__main__':
    main()
