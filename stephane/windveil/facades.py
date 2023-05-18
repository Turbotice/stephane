
import numpy as np
import pylab as plt
import glob
import os
import socket
import platform
import mpmath as math
import cv2
import csv

#Scipy modules
import scipy.integrate as inte
import scipy.special as special
import scipy.interpolate as interp

#Personal modules
import stephane.display.graphes as graphes
import stephane.tools.Smath as smath
#import sympy #symoblic python
	
def read_images(imlist):
    im0 = cv2.imread(imlist[0])
    nx,ny,nc = im0.shape

    n = len(imlist)    
    M = np.zeros((nx,ny,n))

    for filename in imlist:
        j = int(os.path.basename(filename).split('.')[0])
        im = cv2.imread(filename)
        M[...,j-1] = im[...,0]
    return M
    
def display_image(im):
    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(10,10))
    ax.imshow(im)
    return fig,ax
    
def get_scaleF_fps(filename, h_c, s_c, z_c):
    rows = []
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            rows.append(row)
    rows = np.asarray(rows)
    header = rows[0,:]
    scales = rows[1:,:]
    print(header,scales)
    
    movies = [s.split('_') for s in scales[:,0]]
    parts = {}
    for i,movie in enumerate(movies):
        d={}
        h=int(movie[0])
        scene=int(movie[1])
        zone=int(movie[2])
        
        if h == h_c and scene == s_c and zone == z_c:
            fx = float(scales[i,1].replace(',','.'))
            ft = 1/float(scales[i,2].replace(',','.'))
            fps = float(scales[i,2].replace(',','.'))
            break
    return fx, ft, fps
    
    
def demod(t,s, fexc):
    """
    Demodulate a signal at a precise frequency, 
    for instance the frequency "fexc" of a vibrating bath

    :param: 
        * t: is a temporal vector field
        * s: is a 3D (X,Y,T) signal to be demodulated 

    :return: 
        c : (X,Y) is a 2D complex field 
    """
    c = np.mean(s*np.exp(-1j * 2 * np.pi * t[None,None,:] * fexc),axis=2)
    return c
    
def compute_fft_t(M, facq):

    p = 12
    TF = np.fft.fft(M,axis=2,n=2**p)
    TF = TF[...,:2**(p-1)]
    TF_t = np.mean(np.abs(TF),axis=(0,1))

    fmax = facq/2
    f = np.linspace(0,fmax,2**(p-1))
    
    Z = TF_t*f
    fc = 5#upper bound
    Z = Z[f<fc]
    print(f.shape)
    print(Z.shape)
    
    imax = np.argmax(Z)
    f0  = np.round(f[imax],decimals=2)
    print(f0)
    Imax = TF_t[imax]*f0

    return f,TF_t,f0,Imax
    
def display_fft(f,TF_t,f0,Imax,title):
    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(10,10))
    ax.plot(f,TF_t*f)
    plt.xscale('log')
    plt.yscale('log')

    ax.plot(f0,Imax,'rx')
    figs = graphes.legende('$f$ (Hz)',r'$\hat I$',title,ax=ax)
    return figs
    
        
def time_axis(M,facq):
    dt = 1/facq
    nx,ny,n = M.shape
    T = n*dt
    t = np.arange(0,T,dt)
    return t
    
def display_filtered(M,f0,facq):
    t = time_axis(M,facq)

    freqs = [f0/2,3*f0/4,f0,5*f0/4,3*f0/2]
    nc = len(freqs)
    fig,axs = plt.subplots(nrows=1,ncols=nc,figsize=(30,20))

    for i,f in enumerate(freqs):
        f = np.round(f,decimals=2)
        data = demod(t,M,f)
        axs[i].imshow(np.real(data))
    
        tit = '$f_0 =$'+str(f)+'Hz'
        axs[i].set_title(tit)
    tit = '$f_0 =$'+str(freqs[0])+'Hz'
    figs = graphes.legende('X (pix)','Y (pix)',tit,ax=axs[0])
    return figs

def process_movie(imlist, baseFpsName, h_c, s_c, z_c, title, savefolder):
    fx, ft, facq = get_scaleF_fps(baseFpsName, h_c, s_c, z_c)
    M = read_images(imlist)
    fig,ax = display_image(M[...,0])
    figs = graphes.legende('X (pix)','Y (pix)',title,ax=ax)
    graphes.save_figs(figs,savedir=savefolder,prefix='im1_')    
    #plt.show()
    
    f,TF_t,f0,Imax = compute_fft_t(M, facq)
    figs = display_fft(f,TF_t,f0,Imax,title)
    graphes.save_figs(figs,savedir=savefolder)    
    #plt.show()
    
    print(f0)
    figs = display_filtered(M,f0,facq)
    graphes.save_figs(figs,savedir=savefolder)    
    #plt.show()
    
    #t = time_axis(M)
    #Res = compute_rd(M,t)
    #figs = display_rd(Res)
    #graphes.save_figs(figs,savedir=savefolder)    
        
def display_rd(Res):
    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(10,10))
    for f0 in Res.keys():
        ax.plot(f0,Res[f0]['K'],'ko')
#plt.axis([0,6.5,0,0.07])
    #a = 0.009    
#    fs = np.linspace(0,6,100)
#plt.plot(fs,fs*a,'r--')
    figs = graphes.legende('$f$ (Hz)','$k$ (a.u.)','')
    return figs
    
def compute_rd(M,t):
    p0=10
    freqs = np.linspace(0.5,6,20)
    kmax = 1
    Res = {}
    for i,f0 in enumerate(freqs):
        f0 = np.round(f0,decimals=2)
        print(f0)

        Y = np.real(demod(t,M,f0))
        nx,ny = Y.shape    
        p = np.max([np.ceil(np.log2(np.max([nx,ny]))),p0])

        bx = int((2**p-nx)/2)
        by = int((2**p-ny)/2)

        wx = np.hanning(nx)
        wy = np.hanning(ny)
        W = wy[None,:]*wx[:,None]

        Y = Y*W
    
        Ypad = np.pad(Y, [(bx,bx),(by,by)], mode='constant')
        nx,ny = Ypad.shape

        kx = np.linspace(-kmax,kmax,nx)
        ky = np.linspace(-kmax,kmax,ny)
        [Ky,Kx] = np.meshgrid(ky,kx)
        K = np.sqrt(Kx**2+Ky**2)
    
        TF_xy = np.fft.fftshift(np.fft.fft2(Ypad,s=None,norm=None))

#    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(10,15))

        Z = np.abs(TF_xy)*K**(1/4)
        v = np.max(Z, axis=(0,1))
        ind = np.where(Z==v)
        i = ind[0][0]
        j = ind[1][0]
        Res[f0]={}
    
        Res[f0]['K']=K[i,j]
        Res[f0]['f']=f0
    
    return Res
#    print(Kx[i,j],Ky[i,j])
    #sc = ax.imshow(W)
#    sc = ax.pcolormesh(Kx,Ky,np.log(Z),vmin=0,vmax=8)
#    plt.plot(Kx[i,j],Ky[i,j],'rx')
#    plt.colorbar(sc)
    
def compute_fft_xt(M,fx,facq):
    p0=10
    nx,ny,nt = M.shape
    if np.mod(nt,2)==1: #use an even number of images, to pad to the next power of 2 (or to the p0-th power of 2)
        M=M[...,:-1]
        nt=nt-1
    if np.mod(nx,2)==1: #use an even number of images, to pad to the next power of 2 (or to the p0-th power of 2)
        M=M[:-1,...]
        nx=nx-1
    if np.mod(ny,2)==1: #use an even number of images, to pad to the next power of 2 (or to the p0-th power of 2)
        M=M[:,:-1,:]
        ny=ny-1  
    print('nx,ny,nt :',nx,ny,nt)
    kmax = 2 * np.pi / fx

    px = int(np.max([np.ceil(np.log2(nx)),p0]))
    py = int(np.max([np.ceil(np.log2(ny)),p0]))
    pt = int(np.max([np.ceil(np.log2(nt)),p0]))

    bx = int((2**px-nx)/2)
    by = int((2**py-ny)/2)
    bt = int((2**pt-nt)/2)

    wx = np.ones(nx)
    wy = np.hanning(ny)
    wt = np.hanning(nt)

    W = wx[:,None,None]*wy[None,:,None]*wt[None,None,:]
    Y = M*W
        
    Ypad = np.pad(Y, [(0,0),(by,by),(bt,bt)], mode='constant')

    kx = np.linspace(-kmax,kmax,2**px)
    ky = np.linspace(-kmax,kmax,2**py)

    fmax = facq/2
    f = np.linspace(-fmax,fmax,2**pt)
    [F,Ky] = np.meshgrid(f,ky)
        
    TF_yt = np.fft.fftshift(np.fft.fft2(Ypad,axes=(1,2)))
    TF_yt_moy = np.mean(np.abs(TF_yt),axis=0)

    return F,Ky,TF_yt_moy
    
def display_fft_xt(F,Ky,TF_yt,title):    

    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(10,10))
    sc = ax.pcolormesh(Ky,-F,np.log10(TF_yt),vmin=4,vmax=6,shading='gouraud')
    cbar = plt.colorbar(sc)
    cbar.set_label(r'$\hat I$', rotation=0,fontsize=18)

    plt.axis([0,0.1,0,8])
    figs = graphes.legende('$k_x$ (a.u.)','$f$ (Hz)',title,ax=ax)
    
    return figs
    
