# encoding: utf-8
#
#Copyright (C) 2017, P. R. Wiecha
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
pyGDM core routines

"""
from __future__ import print_function
from __future__ import absolute_import

import numpy as np

import gc
import warnings
import copy
import time

from .pyGDMfor import setupmatrix as forSetupmatrix
from .pyGDMfor import dysonseq as forDysonSeq
from .pyGDMfor import propa_sp_decay as forDecay




## (on linux) Set Stacksize for enabling passing large arrays to the fortran subroutines
import platform
if platform.system() == 'Linux':
    import resource
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))


#==============================================================================
# GLOBAL PARAMETERS
#==============================================================================




#==============================================================================
# EXCEPTIONS
#==============================================================================
class CGnoConvergence(Exception):
    pass







#==============================================================================
# Simulation container class
#==============================================================================
class simulation(object):
    """
    Bases: object
    
    Main GDM simulation container class
    
    Defines a linear GDM simulation. Contains information on: 
        - *struct* : :class:`.structures.struct`:
            - the geometry of the nano structure 
            - its dielectric function
            - its environment
        - *efield* : :class:`.fields.efield`
            - the incident field and the wavelenghts 
            - possibly further incident field configuration 
    
    Parameters
    ----------
    
    struct : :class:`.structures.struct`
        structure object
        
    efield : :class:`.fields.efield`
        fundamental field
        
    dtype : (optional) `str`, default: 'f'
        precision of simulation
    
    
    """
    __name__ = "pygdm2 simulation"
    
    def __init__(self, struct, efield, dtype='f'):
        """Initialization"""
        
        ## --- struct includes: geometry, material(s), environment
        self.struct = struct
        
        ## --- efield includes: field_generator function, wavelengths, optional kwargs
        self.efield = efield
        
        ## --- precision
        if dtype in ['f', 'F']:
            self.dtypef = np.float32
            self.dtypec = np.complex64
        elif dtype in ['d', 'D']:
            self.dtypef = np.float64
            self.dtypec = np.complex128
        self.efield.setDtype(self.dtypef, self.dtypec)
        self.struct.setDtype(self.dtypef, self.dtypec)
        
        
        ## --- initialize unevaluated data to `None` (postprocessing data)
        self.E = None   # placeholder: scattered fields inside structure
        self.S_P = None # placeholder: decay-rate tensors
    
    
    def __repr__(self):
        from . import tools
        return tools.print_sim_info(self, prnt=False)
    
    
    def __eq__(self, other):
        ## identical geometries, identical field_kwargs keys, wavelengths, 
        ##     material, n1
        if (np.sum(np.abs(self.struct.geometry - other.struct.geometry))==0 and 
                np.sum(np.abs(self.efield.wavelengths - other.efield.wavelengths))==0 and 
                self.efield.kwargs.keys() == other.efield.kwargs.keys() and 
                self.struct.material[0].__name__ == other.struct.material[0].__name__ and 
                self.struct.n1 == other.struct.n1 and 
                self.struct.n2 == other.struct.n2 and 
                self.struct.n3 == other.struct.n3 and 
                self.struct.step == other.struct.step):
            return True
        else:
            return False
        
        
        
     


#==============================================================================
# scattered fields
#==============================================================================
def scatter(sim, method='lu', 
              cgKwargs={}, cg_recycle_pc=True, pc_method='ilu', pc_recalc_thresh=0.5,
              which_propagator=1, 
              multithreaded=False, Nprocesses=None, verbose=True):
    """Perform a linear scattering GDM simulation
    
    Calculate the electric field distribution inside a nano-structure.
    
    Parameters
    ----------
    sim : :class:`.simulation`
        simulation description
    
    method : string, default: "lu"
        inversion method. One of ["lu", "numpyinv", "scipyinv", "pinv2", "superlu", "cg", "pycg", "dyson"]
         - "lu" LU-decomposition (`scipy.linalg.lu_factor`)
         - "numpyinv" numpy inversion (`np.linalg.inv`, if numpy compiled accordingly: LAPACK's `dgesv`)
         - "scipyinv" scipy default inversion (`scipy.linalg.inv`)
         - "pinv2" is usually slower (req. `scipy.linalg.pinv2`)
         - "superlu" often has a <N^3 efficieny but is very expensive in memory (`scipy.sparse.linalg.splu`)
         - "cg" and "pycg" use iterative conjugate gradient solving, scale with N^2. Not appropriate for many field configs per wavelength! (req. `scipy` or `pyamg`)
         - "dyson" uses a dyson sequence. Only solver that does not depend on external libraries
         - "cuda" uses a CUDA-capable GPU for matrix inversion. 
        
    cgKwargs : dict, default: {}
        keywords passed to conjugate-gradient method, if used 
    
    cg_recycle_pc : bool, default: True
        Use same Preconditioner for all wavelengths (default: True)
        Remark: For large dispersion / large wavelength differences cg_recycle_pc=True 
        might slow down convergence significantly.
        Buy mostly this will speed up the Calcuation.
    
    pc_method : str, default 'ilu'
        Preconditioning method. 
        'ilu': scipy incomplete LU, 
        'lu': scipy complete LU (exact, but speed-imporvements for nearby wavelengths), 
        'amg' pyAMG amg, 
        'none': No preconditioning
    
    PCrecalcThresh : float, default 0.5
        Preconditioning recalculation time threshold.
        If speedup of PC-recycling falls below this threshold, recalculate 
        PC on next wavelength.
        
    which_propagator : int, default 1
        Which propagator to use for inversion. default "1": non-retarded "123" propagator
        with substrate, center medium (with structure), cladding.
        "2": electric-magnetic mixed propagator (only vacuum)
        
    multithreaded : bool, default: False
        Whether to use multi-threading for multi-incident field processing (at each wavelength).
        Requires "pathos". BNy default, use only for structures < 2000 meshpoints to avoid
        memory overflow. You can force it for all structure sizes using multithreaded="force".
    
    Nprocesses : int, default: None
        if "multithreaded"==True, specifies number of processes. if "None": automatic
        
    verbose : bool, default False
        Print timing info to stdout
    
      
    Returns
    -------
    E : list of lists
        list consists of incident field config and the electric field in 
        structure (total complex electric fields: E0 + E_scat).
        Each element of the list is composed as follows, where Exi is the x 
        component of the complex, total electric field at meshpoint i:
           
        elements : 
            [`dict`: kwargs of incident efield, 
             `list`: field as list of tuples [[Ex1,Ey1,Ez1], [Ex2,Ey2,Ez2], ...] ]
        
    Notes
    -----
    - The complex electric fields inside the structure are also copied into the 
      :class:`.simulation` instance as attribute `simulation.E`
    
    - For details on the concept of the generalized propagator, see e.g.:
      Martin, O. J. F. & Girard, C. & Dereux, A. **Generalized Field Propagator 
      for Electromagnetic Scattering and Light Confinement.**
      Phys. Rev. Lett. 74, 526–529 (1995).
    
    - The `scipy` solvers (like 'lu', 'ilu' and 'cg') run parallelized if BLAS
      is compiled with multithreading support. See:
      http://scipy-cookbook.readthedocs.io/items/ParallelProgramming.html#use-parallel-primitives
      (website called 05/2017)
      
    - To limit the number of threads for the multi-threaded parallelized parts, 
      you might do something like explained in: 
      https://stackoverflow.com/questions/29559338/set-max-number-of-threads-at-runtime-on-numpy-openblas
      (website called 06/2017)
    
    - multi-threaded incident field processing (generalized propagator * E0) requires
      "pathos" (https://github.com/uqfoundation/pathos)

        
    """
    if method.lower() not in ["numpyinv", "scipyinv", "lu", "superlu", 
                                       "pinv2", "cg", "pycg", "dyson", "cuda"]:
        raise ValueError('Error: Unknown solving method. Must be one of' +
                         ' ["lu", "numpyinv", "scipyinv", "pinv2", "superlu",'+
                         ' "cg", "pycg", "dyson", "cuda"].')
    field_generator = sim.efield.field_generator
    wavelengths = sim.efield.wavelengths
    
    scattered_fields = []
    PC = None; PCreset = True
    
    for i_wl, wavelength in enumerate(wavelengths):
        if verbose: t0=time.time()
        
        ## --- evaluate polarizabilities and normalization terms at "wavelength"
        sim.struct.getPolarizability(wavelength)
        sim.struct.getNormalization(wavelength)
        
        ## --- construct matrix
        if method.lower() in ["lu", "numpyinv", "scipyinv", "superlu", 
                                                "pinv2", "cg", "pycg", "cuda"]:
            as_csc = True if method.lower() == 'superlu' else False
            CAM0 = get_side_by_side(sim, wavelength=wavelength, invertible=True, 
                                    times_alpha=True, as_csc=as_csc, which_propagator=which_propagator)
        else:
            CAM0 = None
        
#==============================================================================
#         INVERSION / EVALUATION
#==============================================================================
        ## ============== Exact Inversion ==============
        if method.lower() in ["lu", "numpyinv", "scipyinv", "superlu", 
                                                   "pinv2", "dyson", "cuda"]:
            K = get_general_propagator(CAM0, method=method, sim=sim, 
                                       wavelength=wavelength)
            del CAM0; gc.collect()
            
            if verbose: print('timing {:.2f}nm - inversion: {:.1f} ms,'.format(
                                    wavelength, 1000.*(time.time()-t0)), end='')
            t1 = time.time()
            
            ## --- At fixed wavelength: Use generalized propagator on all incident field parameters
            def generalized_propagator_operation(field_kwargs, K, sim, wavelength):
                E0 = field_generator(sim.struct, wavelength, **field_kwargs)
                E0_supervec = _fieldListToSuperVector(E0)
                
                ## --- generalized propagator times incident field:
                if method.lower() == 'superlu':
                    E = K.solve(E0_supervec)
                elif method.lower() == 'lu':
                    import scipy.linalg as la
                    E = la.lu_solve(K, E0_supervec)
                else:
                    E = np.dot(K, E0_supervec)
                
                E = _superVectorToFieldList(E)
                kwargs_final = copy.deepcopy(field_kwargs)
                kwargs_final["wavelength"] = wavelength
                return [kwargs_final, E]
            
            if multithreaded and str(multithreaded).lower() != 'force' and len(sim.struct.geometry)>2000:
                warnings.warn("structure contains more than 2000 meshpoints, deactivating multithreaded field-evaluation." + 
                              "If you wish to use multithreaded generalized propagator evaluation, uset argument `multithreaded` = 'force'.")
                multithreaded = False
                
            if multithreaded:
                try: 
                    import pathos
                    from pathos.multiprocessing import ProcessingPool as Pool
#                    from pathos.threading import ThreadPool as Pool
#                    from pathos.pp import ParallelPool as Pool
                    def func(arg):
                        return generalized_propagator_operation(arg, K, sim, wavelength)
                    if Nprocesses is None:
                        Nprocesses = pathos.multiprocessing.cpu_count()
                    pool = Pool(Nprocesses); pool.clear()
                    scattered_fields_tmp = np.array(pool.map(func, sim.efield.kwargs_permutations))
                    pool.close(); pool.join()
                    for scatfield in scattered_fields_tmp:
                        scattered_fields.append(scatfield)
                except ImportError:
                    warnings.warn("Multi-threaded incident field processing per wavelength"+
                                  " requires the 'pathos' librabry. Seems not to be installed." +
                                  " Falling back to sequential processing.")
                    multithreaded = False
            
            if not multithreaded:
                for field_kwargs in sim.efield.kwargs_permutations:
                    scattered_fields.append(generalized_propagator_operation(
                                                 field_kwargs, K, sim, wavelength))
#                del K; gc.collect()
        
        
        ## ============== Conjugate Gradients ==============
        elif method.lower() in ["cg", "pycg"]:
            if len(sim.efield.kwargs_permutations) > 10:
                warnings.warn("Efficiency warning: Many field-configurations" +
                              " per wavelength (N_conf={})! Conjugate gradients" +
                              " will probably be very slow.".format(
                                          len(sim.efield.kwargs_permutations)))
            if cg_recycle_pc==False: PC = None
            tPCreset = time.time()
            
            for field_kwargs in sim.efield.kwargs_permutations:
                E0 = field_generator(sim.struct, wavelength, **field_kwargs)
                E0_supervec = _fieldListToSuperVector(E0)
                E, PC, STATUS = get_efield_by_cg(CAM0, E0_supervec, PC=PC, 
                                              method=method, pc_method=pc_method, 
                                              **cgKwargs)
                
                if STATUS != 0: # on cgs convergence fail --> exact LU-inversion
                    warnings.warn("CG convergence warning: Conjugate gradients" +
                                  " did not converge. Trying LU instead.")
                    ## PC == K: Use as next preconditioner afterwards (avoid resetting PC).
                    PC = get_general_propagator(CAM0, method="LU", sim=sim, 
                                              wavelength=wavelength, 
                                              retLinearOperator=1)
                    E = PC*E0_supervec
                    tPCreset=time.time()
                    
                E = _superVectorToFieldList(E)
                kwargs_final = copy.deepcopy(field_kwargs)
                kwargs_final["wavelength"] = wavelength
                scattered_fields.append([kwargs_final, E])
            
            ## Check last CG duration: If > pc_recalc_thresh * Preconditionung-time: 
            ## recalculate PC in next step
            if cg_recycle_pc:
                if PCreset:
                    PCreset = False
                    tCG0 = time.time() - tPCreset
                elif time.time()-tPCreset > pc_recalc_thresh*tCG0:
                    PCreset = True
                    PC = None
                    if verbose: print("   Slow convergence (limit {:.1f}ms) " + \
                                      "--> Recalc. PC on next iter.\n   --> ".format(
                                                  pc_recalc_thresh*tCG0*1000), end='')
        
        if verbose: print("repropagation: {:.1f}ms ({} field configs), total: {:.1f} ms".format(
                                            1000.*(time.time()-t1), len(sim.efield.kwargs_permutations), 
                                            1000.*(time.time()-t0)))
            
    
    gc.collect()
    
    sim.E = scattered_fields
    return scattered_fields
#    return CAM0   # tesing only


        
def scatter_mpi(sim, verbose=False, multithreaded=False, scatter_verbose=False, **kwargs):
    """MPI wrapper to :func:`.scatter` for embarrassingly parallel calculation of spectra
    
    *requires:* **mpi4py**
    
    run with "mpirun -n X python scriptname.py", where `X` is the number of 
    parallel processes (ideally an integer divisor of the number of wavelengths)
    
    
    Parameters
    ----------
    sim : :class:`.simulation` 
        simulation description
    
    multithreaded : bool, default: False
        Whether to use multi-threading for multi-incident field processing (at each wavelength).
        Requires "pathos". **warning: use with caution together with MPI!**
    
    verbose, scatter_verbose: bool, default: False
        turns on some mpi-routine info printing, respectively controls verbose setting for :func:`.scatter`
    
    **kwargs : 
        all kwargs are passed to :func:`.scatter`


    Notes 
    -----
    - On single machines it is usually easier to install `scipy` 
      compiled with parallel BLAS (parallel LU / CG routines). Usually the
      parallel BLAS is will be already installed automatically. Try to not use 
      both parallelisation techniques simultaneously unless properly
      configured for instance via a batch script (e.g. `SLURM`). 
      *Overloading the CPUs will usually result in decreased calculation speed.*
    
    - see :func:`.scatter` for documentation
    
    - by default, will pass `multithreaded = False` to :func:`.scatter`
    
    """
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    nprocs, rank = comm.Get_size(), comm.Get_rank()

    

    ## --- create list of jobs and split in equal parts depending on `nprocs`
    def split(jobs, nprocs):
        return [jobs[i::nprocs] for i in range(nprocs)]
    
    if comm.rank == 0:
        if nprocs == 1:
            warnings.warn("Executing only one MPI process! Should be run using" +
                          " e.g. 'mpirun -n X python scriptname.py', where X" +
                          " is the number of parallel processes.")
        if verbose: 
            print("")
            print("number of MPI processes:        ", nprocs)
            print("number of wavelengths:          ", len(sim.efield.wavelengths))
            print("number of wavelengths / process:", int(np.ceil(len(sim.efield.wavelengths) / float(nprocs))))
            print("")
        
        if verbose: print("Generating and splitting jobs... ", end='')
        jobs_all = []
        for i, wl in enumerate(sim.efield.wavelengths):
            ## --- generate simulation objects for each individual wavelength
            from . import fields
            _sim = copy.deepcopy(sim)
            _efield = fields.efield(_sim.efield.field_generator, [wl], _sim.efield.kwargs)
            _efield.setDtype(_sim.dtypef, _sim.dtypec)
#            _sim.efield.wavelengths = [wl]
            _sim.efield = copy.deepcopy(_efield)
            jobs_all.append(_sim)
        jobs = split(jobs_all, nprocs)
        if len(np.unique([len(i) for i in jobs])) > 1:
            warnings.warn("Efficiency warning: Number of wavelengths ({}) ".format(
                                                len(sim.efield.wavelengths)) + 
                          "not divisable by Nr of processes ({})!".format(nprocs))
        if verbose: print("Done.")
    else:
        jobs = None
    
    
    ## --- Scatter jobs across processes and perform GDM simulations for each wavelength
    jobs = comm.scatter(jobs, root=0)
    
    results = []
    for job in jobs:
        if verbose: print(" process #{}: Calculating wavelength" + \
                               " {}nm".format(rank, job.efield.wavelengths[0]))
        scattered_field = scatter(job, multithreaded=multithreaded, verbose=scatter_verbose, **kwargs)
        for _scatf in scattered_field:
            results.append(_scatf)
    
    
    ## --- Gather results on rank 0
    results = MPI.COMM_WORLD.gather(results, root=0)
    
    if comm.rank == 0:
        if verbose: print("All simulations done. Recombining... ", end='')
        ## --- recombine data and sort by wavelength
        results = [i for temp in results for i in temp]
        results = sorted(results, key=lambda k: k[0]['wavelength'])
        sim.E = results
        if verbose: print("Done.")
    
    return results
    




# =============================================================================
# Decay rate calculation
# =============================================================================


def decay_rate(sim, method='lu', verbose=False):
    """Calculate the decay rate of a dipole emitter
    
    Calculate the propagator necessary to derive the change of decay rate of
    an electric or magnetic dipolar emitter in the vicinity of a photonic
    nanostructure.
    The result of this routine can be used to calculate the actual decay rate
    for a dipole transition of any orientation / amplitude using 
    :func:`.linear.decay_eval`.
    
    Parameters
    ----------
      sim : :class:`.simulation`
        simulation description
          
      method : string, default: "lu"
        inversion method. One of ["lu", "numpyinv", "scipyinv", "pinv2", "superlu", "dyson"]
         - "lu" LU-decomposition (`scipy.linalg.lu_factor`)
         - "numpyinv" numpy inversion (`np.linalg.inv`, if numpy compiled accordingly: LAPACK's `dgesv`)
         - "scipyinv" scipy default inversion (`scipy.linalg.inv`)
         - "pinv2" is usually slower (req. `scipy.linalg.pinv2`)
         - "superlu" often has a <N^3 efficieny but is very expensive in memory (`scipy.sparse.linalg.splu`)
         - "dyson" uses a dyson sequence. Only solver that does not depend on external libraries
         - "cuda" uses a CUDA-capable GPU for matrix inversion. 
          
      verbose : bool default=False
          print some info
    
    
    Returns
    -------
      list of lists:  each element of the main list contains [wavelength, S_P].
              `S_P` again is a list of the 3x3 tensors S_P^EE (or S_P^BB) for 
              each map-position (EE: electric dipole, BB: magnetic dipole)
      
    
    Notes
    -----
    `sim` must contain either an electric or magnetic dipole emitter as 
    fundamental field. Its orientation and amplitude will however be ignored.
    These need to be specified later, when the actual evaluation is done using
    :func:`.linear.decay_eval`
    
    For detailed information about the underlying formalism, see:
    Wiecha, P. R., Girard, C., Cuche, A., Paillard, V. & Arbouet, A. 
    **Decay Rate of Magnetic Dipoles near Non-magnetic Nanostructures.** 
    arXiv:1707.07006 (2017)

      
    """
    
    if method.lower() not in ["numpyinv", "scipyinv", "lu", "superlu", 
                                               "pinv2", "dyson", "cuda"]:
        raise ValueError('Error: Unknown solving method. Must be one of' +
                         ' ["lu", "numpyinv", "scipyinv", "pinv2",' +
                         ' "superlu", "dyson", "cuda"].')
    
    field_generator = sim.efield.field_generator
    wavelengths = sim.efield.wavelengths
    xyz = [[pos['x0'], pos['y0'], pos['z0']] for pos in sim.efield.kwargs_permutations]
    xmap, ymap, zmap = np.transpose(xyz)
    
    dp_orient = [[pos['mx'], pos['my'], pos['mz']] for pos in sim.efield.kwargs_permutations]
#    if len(sim.efield.kwargs["mx"]) > 1 or len(sim.efield.kwargs["my"]) > 1 or len(sim.efield.kwargs["mz"]) > 1:
#    if len(np.unique(dp_orient, axis=0)) > 1:
    if len([x for x in dp_orient if dp_orient.count(x) >= 2]) > 1:
        warnings.warn("The dipole orientation is configured multiple times. " + 
                      "This setting will be ignored by `core.decay_rate`. " +
                      "Please use `linear.decay` to compute the decay-rates for " +
                      "several dipole orientations.")
        
    from . import fields
    if field_generator == fields.dipole_electric:
        magnetic = 0
        dipole_type = 'electric'
    elif field_generator == fields.dipole_magnetic:
        magnetic = 1
        dipole_type = 'magnetic'
        if sim.struct.n1 != sim.struct.n2 or sim.struct.n2 != sim.struct.n3:
            raise ValueError("Substrate or cladding layers are not supported in " + 
                             "magnetic dipole decay rate simulations until " +
                             "now. Please use a homogeneous environment.")
    else:
        raise ValueError("Wrong incident field: `decay_rate` requires the " + 
                         "incident field to be " + 
                         "either an electric or a magnetic dipole emitter. " +
                         "Please use `fields.dipole_electric` or " +
                         "`fields.dipole_magnetic`.")
    
    xm, ym, zm = sim.struct.geometry.T
    
    SBB_spectral = []
    for i_wl, wavelength in enumerate(wavelengths):
        if verbose: 
            t0=time.time()
            print("Wavelength: {}nm - {} dipole".format(wavelength, dipole_type))
        
        ## --- evaluate polarizabilities and normalization terms at "wavelength"
        sim.struct.getNormalization(wavelength)
        alpha = sim.struct.getPolarizability(wavelength)
        
        ## --- construct matrix
        if method.lower() in ["lu", "numpyinv", "scipyinv", "superlu", "pinv2", "cuda"]:
            as_csc = True if method.lower() == 'superlu' else False
            CAM0 = get_side_by_side(sim, wavelength=wavelength, invertible=True, 
                                    times_alpha=True, as_csc=as_csc)
        else:
            CAM0 = None
        
        ## --- Inversion: General Propagator
        if method.lower() in ["lu", "numpyinv", "scipyinv", "superlu", 
                                                             "pinv2", "dyson", "cuda"]:
            K = get_general_propagator(CAM0, method=method, sim=sim, 
                                       wavelength=wavelength)
            if verbose:
                print("  - inversion:            {:.3f}s".format(time.time()-t0))
                t0=time.time()
            del CAM0; gc.collect()
            
            ## --- generalized propagator: explicit matrix
            if method.lower() == 'superlu':
                K = K.solve(np.identity(3*len(xm)))
            elif method.lower() == 'lu':
                import scipy.linalg as la
                K = la.lu_solve(K, np.identity(3*len(xm)))
            else:
                pass
        
        
        
        ## --- decay-rate using multi-threaded fortran routine
        SP = forDecay(sim.struct.step, xm,ym,zm, 
                      sim.struct.n1, sim.struct.n2, sim.struct.n3,
                      wavelength, 
                      xmap, ymap, zmap,
                      magnetic, K, alpha)
        
        SBB = [SP[i].reshape( 3,3 ) for i in range(len(SP))]
        
        if verbose:
            print("  - decay repropagation:  {:.3f}s".format(time.time()-t0))
            t0=time.time()
            
        SBB_spectral.append([wavelength, SBB])
    
    sim.S_P = SBB_spectral
    
    return SBB_spectral
    
    
























#==============================================================================
# Matrix operations
#==============================================================================
def get_side_by_side(sim, wavelength, invertible=True, times_alpha=True, 
                         as_csc=True, which_propagator=1):
    """Build side-by-side matrix CA0 for the structure at given wavelength
    
    Parameters
    ----------
    sim : :class:`.simulation`
        simulation description
        
    wavelength: float
        Wavelength at which to calculate susceptibility matrix (in nm)
        
    invertible: bool, default: True
        return invertible matrix (I-CA0)
        
    times_alpha: bool, default: True
        multiply by alpha. If True: CA0 = alpha.G; else CA0 = G
        
    as_csc: bool, default: True
        return as csc sparse matrix format
    
    which_propagator : int, default 1
        Which propagator to use for inversion. default "1": non-retarded "123" propagator
        with substrate, center medium (with structure), cladding.
        "2": electric-magnetic mixed propagator (only vacuum)
    
    Returns
    -------
    CA0 : array-like
        return the side-by-side matrix CA0 ("S"). 
        Inverse of CAM0=(I-CA0) is generalized propagator
    
    
    Notes
    -----
    For the analytical expression of the asymptotic propagators with substrate, 
    see e.g.: 
    Girard, C. **Near fields in nanostructures.** 
    Reports on Progress in Physics 68, 1883–1933 (2005).
    """
    xm, ym, zm = sim.struct.geometry.T
    
    CA0 = forSetupmatrix(alambda=wavelength, space=sim.struct.spacing, 
                          xm=xm,ym=ym,zm=zm,
                          cap=sim.struct.alpha,
                          cn1=sim.struct.n1, cn2=sim.struct.n2, cn3=sim.struct.n3,
                          cnorm=sim.struct.cnorm,
                          timesalpha=times_alpha,
                          propagator=which_propagator) 
    ## propagator "1": 1-2-3, separated, object MUST be in zone 2
    ## propoagator "2": testing: elec-mag mixed propagator (vacuum)
    
    N = np.shape(CA0)[0]
    if not invertible:
        CA0 = np.asfortranarray(np.identity(N) - CA0, dtype=sim.dtypec)
    if as_csc:
        from scipy.sparse import csc_matrix

        CA0 = csc_matrix(CA0, shape=(N, N))
    
    return CA0


        
def get_general_propagator(CAM0, method='lu', sim=None, wavelength=None, 
                         return_linear_operator=False, 
                         return_susceptibility=False):
    """Invert Matrix CAM0
    
    Parameters
    ----------
    CAM0 : array-like
        Matrix to invert (I-CA0). As returned by :func:`.get_side_by_side` 
        ("dyson" calculates CAM0 itself, may be set to `None` in that case)
                 
    method : string, default: "lu"
        inversion method. One of ["lu", "numpyinv", "scipyinv", "pinv2", "superlu", "dyson"]
         - "lu" LU-decomposition (`scipy.linalg.lu_factor`)
         - "numpyinv" numpy inversion (`np.linalg.inv`, if numpy compiled accordingly: LAPACK's `dgesv`)
         - "scipyinv" scipy default inversion (`scipy.linalg.inv`)
         - "pinv2" is usually slower (`scipy.linalg.pinv2`)
         - "superlu" often has a <N^3 efficieny but is very expensive in memory (`scipy.spares.linalg.splu`)
         - "dyson" uses a dyson sequence. Does not depend on external libraries
         - "cuda" uses a CUDA-capable GPU for matrix inversion. 
      
    simDict : dict 
        simulation description, generated from 'genSimDict'
        
    Ilambda : int, default: None
        Wavelength, only required for method "dyson"
        
    retLinearOperator : bool, default: True
        return K as LinearOperator Class
    
    return_susceptibility : bool, default: False
        return the field susceptibility S inside the structure instead of the 
        generalized propagator (K = 1 + chi*S)
        
    
    Returns
    -------
      - K: Inverse of CAM0. Generalized Propagator
      
    Notes
    -----
    For details on the concept of the generalized propagator, see e.g.:
    Martin, O. J. F. & Girard, C. & Dereux, A. **Generalized Field Propagator 
    for Electromagnetic Scattering and Light Confinement.**
    Phys. Rev. Lett. 74, 526–529 (1995).
    """
    
    if return_susceptibility and method.lower() != 'dyson':
        raise ValueError("Field susceptibility can for the moment only be "+
                         "calculated using the 'dyson' solver. Please use 'dyson'.")
    
    ## --- superlu-LU decomposition (scipy.sparse)
    if method.lower() in ["superlu"]:
        import scipy.sparse.linalg as la
        K = la.splu(CAM0)

        ## --- superLU-object can be transformed to a scipy linearoperator by
        if return_linear_operator: 
            _dtype = CAM0.dtype
            N = CAM0.shape[0]
            K = la.LinearOperator(shape=(N, N), matvec=K.solve, dtype=_dtype)
            del CAM0; gc.collect()
    

    ## --- standard scipy.linalg inversion methods
    elif method.lower() in ["numpyinv", "scipyinv", "lu", "pinv2"]:
        if method.lower() in ["numpyinv"]:     # pyGDM2 default
            K = np.linalg.inv(CAM0)
        elif method.lower() in ["scipyinv"]:
            import scipy.linalg as la
            K = la.inv(CAM0, overwrite_a=True)
        elif method.lower() in ["lu"]:
            import scipy.linalg as la
            K = la.lu_factor(CAM0, overwrite_a=True)
        elif method.lower() in ["pinv2"]: 
            import scipy.linalg as la
            K = la.pinv2(CAM0)
        del CAM0; gc.collect()
    
    
    ## --- Dyson sequence (openMP - fortran routine)
    elif method.lower() == "dyson":
        if sim is None:
            raise ValueError("Instance of core.simulation must be provided if using 'dyson' solver.")
        if return_susceptibility:
            return_susceptibility = 1
        else:
            return_susceptibility = 0
        xm, ym, zm = sim.struct.geometry.T
        CAM0 = forDysonSeq(wavelength, sim.struct.spacing, 
                              xm,ym,zm, sim.struct.alpha,
                              sim.struct.n1, sim.struct.n2, sim.struct.n3,
                              sim.struct.cnorm, returnsusc=return_susceptibility)
        
        if return_linear_operator:
            import scipy.sparse.linalg as la
            K = la.aslinearoperator(CAM0)
            del CAM0; gc.collect()
        else:
            K = CAM0
    
    ## --- CUDA based inversion on GPU - EXPERIMENTAL FEATURE
    elif method.lower() == "cuda":
        import pycuda.autoinit
        import pycuda.gpuarray as gpuarray
        import skcuda.linalg as culinalg
        culinalg.init()
        ## convert to cuda array, invert, re-convert to numpy array
        Agpu = gpuarray.to_gpu(CAM0)
        Ainv_gpu = culinalg.inv(Agpu, overwrite=True)
        del CAM0; gc.collect()
        K = Ainv_gpu.get()
        
    else:
        raise ValueError('Invalid inversion method. Must be one of ["numpyinv", "scipyinv", "lu", "pinv2", "superlu", "dyson"].')
    
    return K



def get_efield_by_cg(CAM0, E0, pcTol=2E-3, fill_factor=15, cgsTol=1E-2, 
                  maxiter=200, PC=None, method='cg', pc_method='ilu', 
                  verbose=False):
    """Invert Matrix CAM0
    
    Parameters
    ----------
    CAM0 : array-like
        Matrix to invert (I-CA0). As returned by get_side_by_side. 
    
    E0 : array-like
        Incident electric field, 3N super-vector 
        (you may use :func:`._fieldListToSuperVector`)
    
    pcTol, cgsTol : float, float, defaults: 2E-3 and 1E-2
        tolerances for preconditioning / conjugate gradients
        pcTol > 1: Don't use preconditioning
    
    maxiter : int, default: 500
        Max. iterations for CG
        
    fill_factor : int, default: 15
        Preconditioning Parameter
    
    PC : array-like, default: None
        Optional Preconditer Matrix. If not None, overrides preconditioning.
    
    method : string, default: 'cg'
        iterative solver to use. 
        'cg': scipy stab-cg; 'pycg' pyAMG implementation of stab-cg (threadsafe)
    
    pc_method : string, default: 'ilu'
        Preconditioning method. 
         - 'ilu': scipy incomplete LU, 
         - 'lu': scipy complete LU (exact, but speed-improvements for close 
           wavelengths when recycling), 
         - 'amg' pyAMG amg, 
         - 'none': No preconditioning
    
    Returns
    -------
    E : array-like
    M : array-like, STATUS : int
    
    - E :       Solution of CAM0*E = E0 (3N supervector)
    - M :       Used Preconditioner Matrix (for possible re-use)
    - STATUS :  Status of conj. gradient. (0: converged, !=0: not converged)
    """
    if method.lower() in ["pycg"]:
        from pyamg.krylov._bicgstab import bicgstab as cgsAMG
        cgSolver = cgsAMG
    elif method.lower() in ["cg"]:
        from scipy.sparse.linalg import bicgstab as scipycgs
        cgSolver = scipycgs
    else:
        raise ValueError("Error: Unknown solver for CG.")
        
    N = np.shape(CAM0)[0]
    DTYPE = CAM0.dtype
    
    ## preconditioning
    if PC==None and pcTol > 1. or (pc_method.lower() in ['none', 'false']):
        M = np.identity(N)
    elif PC==None and pcTol <= 1.:
        if verbose: print("Preconditioning...")
        if pc_method.lower() == 'ilu':
            import scipy.sparse.linalg as la
            PCILU = la.spilu(CAM0, drop_tol=pcTol, fill_factor=fill_factor, drop_rule='basic, area')
            M = la.LinearOperator(shape=(N, N), matvec=PCILU.solve, dtype=DTYPE)
        elif pc_method.lower() == 'lu':
            import scipy.sparse.linalg as la
            PCLU = la.splu(CAM0) ## EXACT!!
            M = la.LinearOperator(shape=(N, N), matvec=PCLU.solve)
        elif pc_method.lower() == 'amg':
            from pyamg import smoothed_aggregation_solver
            ml = smoothed_aggregation_solver(CAM0, coarse_solver="pinv2")
            M = ml.aspreconditioner(cycle='V')
    else:
        if verbose: print("Re-use PC...")
        M = PC
    
    if verbose: print("Iterate conjugate gradients...")
    E, STATUS = cgSolver(CAM0, E0, M=M, tol=cgsTol, maxiter=maxiter)
    del CAM0; gc.collect()
    return E, M, STATUS











#==============================================================================
# Internal Helper Functions
#==============================================================================
def _superVectorToFieldList(E):
    """convert complex 3N supervector E to list of N field tuples (Ex,Ey,Ez)"""
    return np.reshape(E, (int(len(E)/3), 3))


def _fieldListToSuperVector(E):
    """convert list of N field tuples (Ex,Ey,Ez) to complex 3N supervector E"""
    return np.reshape(E, (np.product(E.shape)))


def _complexToFortranFloatFieldList(efield, dtype='f'):
    """Convert complex to fortran-compatible float valued lists of Re/Im values
    
    Parameters
    ----------
    efield : np.array of field tuples, complex
        efield list as returned by "scatter" simulation
    
    Returns
    -------
    EX1,EX2, EY1,EY2, EZ1, EZ2 : lists
        1: real part, 2: imag part
    """
    EX, EY, EZ = efield.T
    
    EX1 = np.asfortranarray(EX.real, dtype=dtype)
    EX2 = np.asfortranarray(EX.imag, dtype=dtype)
    EY1 = np.asfortranarray(EY.real, dtype=dtype)
    EY2 = np.asfortranarray(EY.imag, dtype=dtype)
    EZ1 = np.asfortranarray(EZ.real, dtype=dtype)
    EZ2 = np.asfortranarray(EZ.imag, dtype=dtype)
    
    return EX1,EX2, EY1,EY2, EZ1,EZ2


def _sortByParameterConfig(sim, sortList):
    """Sort `sortList` by incident field kwargs configurations using definitions in `sim`
    
    Parameters
    ----------
    sim : :class:`.simulation`
        simulation describtion
    
    sortList : list
        list of fields sorted by incident-field-parameters such as returned e.g. 
        by `pyGDM2.core.scatter`
    
    Returns
    -------
    sortedResults : list of lists
        each list contains a full spectrum with otherwise identical 
        first element, the latter being the incident field's parameter-set
        
        
    """
    Npermutations = len(sortList) / len(sim.efield.wavelengths)
    sortedFields = [ [] for i in range(Npermutations) ]
    
    for i, e in enumerate(sortList):
        sortedFields[i%Npermutations].append(e)
    
    return sortedFields


def _insertInSpectralEfieldFortran(efield, E, ilambda):
    """insert E in spectral efield-array at position (ilambda)
    
    Use for passing field data to parallelized fortran routines.
    - Shape of 'efield': (3, Ndp, Nlambda), complex.
    - Shape of 'E': list of 3-tuples, complex. 
        Example: E = [[Ex1,Ey1,Ez1],  [Ex2,Ey2,Ez2],  ...].
    
    Parameters
    ----------
    efield : np.array, complex
        Spectral E-field array as required by some parallelized fortran
        routines (shape: (3, Ndp, Nlambda, Ntheta), complex)
    
    E : list of 3-tuples, complex
        E-Field, list fo complex 3-tuples: [[Ex1,Ey1,Ez1],  [Ex2,Ey2,Ez2],  ...]
    
    ilambda : int
        index of wavelength to insert in efield 
    
    Returns
    -------
    efield : np.array, complex (shape: (3, Ndp, Nlambda))
        Efield list where field at position 'ilambda' is replaced by E
    """
    S = np.shape(efield)
    if not (0 <= ilambda < S[2]):
        raise ValueError("Invalid Index for Wavelength! Must be Nlambda >= ilambda > 0.")
    
    Ex, Ey, Ez = E.T
    
    for i,(ex,ey,ez) in enumerate(zip(Ex,Ey,Ez)):
        efield[0][i][ilambda] = ex
        efield[1][i][ilambda] = ey
        efield[2][i][ilambda] = ez
        
    return np.asfortranarray(efield, dtype=ex.dtype)





