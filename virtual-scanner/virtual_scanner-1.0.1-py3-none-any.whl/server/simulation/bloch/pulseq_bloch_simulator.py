 # Unit test for direct-from-pulseq bloch simulation

import pulseq_blochsim_methods as blcsim
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import phantom as pht
import multiprocessing as mp
import pulseq_library as psl
import argparse
from math import pi
import os
import datetime


cpath = os.getcwd()
if not (cpath.endswith('Virtual-Scanner')):
    s = cpath.split('src')
    #print('Current working directory is set to: '+s[0])
    os.chdir(s[0])


GAMMA_BAR = 42.5775e6
GAMMA = 2*pi*GAMMA_BAR

if __name__ == '__main__':
    """Parse arguments"""
    parser = argparse.ArgumentParser(description='Bloch simulation parser')
    # Patient id
    parser.add_argument('pat_id',type=str,help="Patient ID")
    # Phantom parameters
    parser.add_argument('pht_type',type=str,help="Type of phantom")# {'brainweb','spherical','NIST','default}
    parser.add_argument('pht_dim',type=int,help='Choose phantom to be 2D or 3D') # 2 - 2D, 3 - 3D
    parser.add_argument('n_ph',type=int,default=16,help="Matrix size of phantom")
    parser.add_argument('fov_ph',type=float,default=0.2,help="Physical size of phantom (m)")
    parser.add_argument('PDs',type=float,nargs=3,help='PD values')
    parser.add_argument('T1s',type=float,nargs=3,help='T1 values (s)')
    parser.add_argument('T2s',type=float,nargs=3,help='T2 values (s)')
    parser.add_argument('dir_ph',type=str,help='Direction for planar phantom (not used in 3D)') # 'x','y', or 'z'

    # Sequence parameters
    ## Geometry
    parser.add_argument('seq_type',type=str,help="Type of sequence")#{'gre','se','irse'}
    parser.add_argument('num_slices',type=int,help="Number of slices")
    parser.add_argument('thk',type=float,help="Slice thickness (m)")# unit [m]
    parser.add_argument('slice_gap',type=float,help="Slice gap (edge-to-edge)") # unit [m]
    parser.add_argument('n',type=int,help="Matrix size")
    parser.add_argument('fov',type=float,help="Field of view of sequence (m)")# unit [m]
    parser.add_argument('enc',type=str,help="Encoding directions")# e.g. 'xyz': fe-x, pe-y, ss-z

    ## Contrast
    parser.add_argument('tr',type=float,help="Repetition time (s)")
    parser.add_argument('te',type=float,help="Echo time (s)")
    parser.add_argument('ti',type=float,help="Inversion time (s)")
    parser.add_argument('fa',type=float,help="Flip angle (deg)")

    ## Extra
    parser.add_argument('b0map',type=int,help="Type of dB0 map") #0 -none; 1- linear; 2- quadratic

    args = parser.parse_args()
    print(args)


    # Make phantom
    myphantom = 0
    if args.pht_type == 'brainweb':
        if args.pht_dim == 3:
            myphantom = pht.BrainwebPhantom('brainweb.npy',dsf=8,make2d=False)
        elif args.pht_dim == 2:
            myphantom = pht.BrainwebPhantom('brainweb.npy',dsf=8,make2d=True,loc=0,dir='z')

    elif args.pht_type == 'spherical':
        print('Making spherical phantom')
        Rs = args.fov_ph * np.array([0.2, 0.35, 0.45])
        if args.pht_dim == 3:
            myphantom = pht.makeSphericalPhantom(n=args.n_ph, fov=args.fov_ph,
                                               T1s=args.T1s, T2s=args.T2s, PDs=args.PDs, radii=Rs)
        elif args.pht_dim == 2:
            loc_vec_dict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1)}
            myphantom = pht.makePlanarPhantom(n=args.n_ph, fov=args.fov_ph,
                                              T1s=args.T1s, T2s=args.T2s, PDs=args.PDs,
                                              radii=Rs, dir=args.dir_ph, # TODO
                                              loc=0) # now, 2D phantom is not moved around
                                              #args.slice_loc*np.array(loc_vec_dict[args.enc[2]]))

    elif args.pht_type == 'cylindrical': #TODO let's make a better phantom with T1, T2, PD varying individually
        print("Making cylindrical phantom")
        myphantom = pht.makeCylindricalPhantom(dim=args.pht_dim, n=args.n_ph, dir=args.dir_ph, loc=0)

    elif args.pht_type == 'NIST':
        myphantom = []
        # myphantom = pht.get_NIST_Phantom()

    else:
        raise ValueError("Phantom type non-existent!")


    # Slice locations # TODO multislice thing

    Ns = args.num_slices
    g = args.slice_gap
    t = args.thk
    slice_locs = np.arange(-(Ns - 1) * (g + t) / 2, Ns * (g + t) / 2, g + t)
    print('Slice locations:',slice_locs)


    if args.seq_type == 'gre':
        myseq = psl.make_pulseq_gre(fov=args.fov,n=args.n,thk=args.thk,fa=args.fa,
                                    tr=args.tr,te=args.te,enc=args.enc,slice_locs=slice_locs,write=False)
    elif args.seq_type == 'se':
        myseq=psl.make_pulseq_se(fov=args.fov,n=args.n,thk=args.thk,fa=args.fa,
                                    tr=args.tr,te=args.te,enc=args.enc,slice_locs=slice_locs,write=False)
    elif args.seq_type == 'irse':
        myseq = psl.make_pulseq_irse(fov=args.fov,n=args.n,thk=args.thk,fa=args.fa,
                                     tr=args.tr,te=args.te,ti=args.ti,enc=args.enc,slice_locs=slice_locs,write=False)
    else:
        raise ValueError("Type of sequence not supported")

    # B0 inhomogeneity
    dBmap = blcsim.get_dB0_map(maptype=args.b0map)

    # Time the code: Tic
    start_time = time.time()
    loc_ind_list = myphantom.get_list_inds()

    # Get seq info
    seq_info = blcsim.store_pulseq_commands(myseq)

    # Initiate multiprocessing pool
    pool = mp.Pool(mp.cpu_count())

    # Multiprocessing simulation
    results = pool.starmap_async(blcsim.sim_single_spingroup, [(loc_ind, GAMMA_BAR*dBmap(myphantom.get_location(loc_ind)), myphantom, seq_info) for loc_ind in loc_ind_list]).get()
    pool.close()
    # Add up signal across all SpinGroups
    raw_signal = np.sum(results,axis=0)

    # Time the code: Toc
    print("Simulation complete!")
    print("Time used: %s seconds" % (time.time()-start_time))


    # Recon and save
    # TODO refine recon, data and image saving, etc.
    # 1. Find image dimension
    # 2. Recon all images
    # 3. store: (a) raw data (b) recon data (c) images (optional) (d) info: slice loc, TI (for now)
    #                                                            in general, varying TR, TE, etc. should be stored (how?)

    # Recon
    if args.seq_type in ['se','gre','irse']: # Cartesian recon
        N = args.n
        im_mat = np.zeros((N, N, Ns), dtype=complex)
        kspace = np.zeros((N, N, Ns), dtype=complex)
        for v in range(len(slice_locs)):
           kspace[:,:,v] = raw_signal[v*N:v*N+N]
           im_mat[:,:,v] = np.fft.fftshift(np.fft.ifft2(kspace[:,:,v]))
           # Save image


        sim_data = {}
        sim_data['kspace'] = kspace
        sim_data['image'] = im_mat
        sim_data['var_info'] = {'locs': slice_locs}
        sim_data['seq_info'] = {'type':args.seq_type,'fa':args.fa,'tr':args.tr,'te':args.te,'slice_dir':args.enc[2]}
        sim_data['pht_info'] = {'type':args.pht_type, 'dim':args.pht_dim}
        if args.seq_type == 'irse':
            sim_data['seq_info']['ti'] = args.ti

        timestamp = time.strftime("%Y%m%d%H%M%S")
        mypath1 = './src/server/simulation/outputs/'+args.pat_id
        if not os.path.isdir(mypath1):
            os.makedirs(mypath1)
        datapath = mypath1+'/DATA_'+args.seq_type.upper()+'_'+timestamp+'.npy'
        np.save(datapath,sim_data)

        # save images in folder
        data = np.load(datapath).all()
        images = data['image']

        for v in range(np.shape(images)[2]):
            plt.axis("off")
            fig = plt.imshow(np.absolute(images[:,:,v]))
            plt.gray()
            fig.axes.get_xaxis().set_visible(False)
            fig.axes.get_yaxis().set_visible(False)
            mypath2 = './src/coms/coms_ui/static/acq/outputs/'+args.pat_id
            if not os.path.isdir(mypath2):
                os.makedirs(mypath2)

            tiopt = 'ms_TI'+str(round(1e3*args.ti)) if args.seq_type == 'irse' else ''
            impath = mypath2+'/IM_'+args.seq_type.upper()+'_'+str(args.enc[2]).upper()+'_TR'+str(round(1e3*args.tr))+\
                    'ms_TE'+str(round(1e3*args.te))+tiopt+\
                    'ms_FA'+str(round(args.fa))+'_'+timestamp+'_'+str(v+1)+'.png'

            plt.savefig(impath, bbox_inches='tight', pad_inches=0, format='png')


        # display (comment off later)
        # mydata = np.load(datapath).all()
        # image = mydata['image']
        # kspace = mydata['kspace']
        # Ns = np.shape(image)[2]
        # a1 = int(np.sqrt(Ns))
        # a2 = int(np.ceil(Ns/a1))
        #
        # plt.figure(1)
        # for v in range(Ns):
        #     plt.subplot(a1,a2,v+1)
        #     plt.imshow(np.absolute(kspace[:,:,v]))
        #     plt.gray()
        #
        # plt.figure(2)
        # for v in range(Ns):
        #     plt.subplot(a1,a2,v+1)
        #     plt.imshow(np.absolute(image[:,:,v]))
        #     plt.gray()
        #
        # plt.show()
