"""

"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment
# pylama: ignore=E0602

chroma_version = USERARG.get('CHROMA_VERSION', '2018')
sm_target      = USERARG.get('SM_TARGET', 'sm_70')

Stage0 += comment(__doc__.strip(), reformat=False)

###############################################################################
# Devel stage
###############################################################################
Stage0.name = 'devel'
Stage0 += baseimage(image='nvidia/cuda:9.0-devel-ubuntu16.04', AS=Stage0.name)

# GNU toolchain
tc = hpccm.toolchain(CC='gcc', CFLAGS='-O3 -std=gnu99',
                     CXX='g++', CXXFLAGS='-g -O3 -std=c++11',
                     CUDA_HOME='/usr/local/cuda')

# Mellanox OFED
mofed = mlnx_ofed()
Stage0 += mofed

# MVAPICH 2.3b
mv2 = mvapich2(configure_opts=['--disable-fortran', '--disable-mcast'],
               prefix='/mvapich/install', version='2.3b')
Stage0 += mv2

# Setup MPI toolchain
mpi_tc = mv2.toolchain
mpi_tc.CFLAGS = '-fopenmp -D_REENTRANT -g -O3 -std=gnu99'
mpi_tc.CXXFLAGS = '-fopenmp -D_REENTRANT -g -O3 -std=c++11 -fexceptions'
mpi_tc.CUDA_HOME = tc.CUDA_HOME

# Temporary hack to get the MPI compilers working
Stage0 += environment(variables={'LD_LIBRARY_PATH': '$LD_LIBRARY_PATH:/usr/lib/x86_64-linux-gnu:/usr/local/cuda/lib64/stubs'})
Stage0 += shell(commands=['ln -s /usr/local/cuda/lib64/stubs/libnvidia-ml.so /usr/local/cuda/lib64/stubs/libnvidia-ml.so.1'])

Stage0 += apt_get(ospackages=['autoconf', 'automake', 'ca-certificates',
                              'cmake', 'flex', 'git', 'libtool', 'libxml2-dev',
                              'm4', 'pkg-config', 'python'])

# Checkout Chroma and all its dependencies
Stage0 += shell(commands=['git config --global url.https://github.com/.insteadOf git@github.com:'])
git = hpccm.git(opts=['--recursive'])

# LLVM
llvm = [git.clone_step(repository='https://github.com/llvm-mirror/llvm',
                       commit='dbbb6c5fc3642987430866dffdf710df4f616ac7',
                       directory='llvm6-trunk', path='/chroma/src'),
        'mkdir -p /chroma/build/llvm6-trunk',
        'cd /chroma/build/llvm6-trunk',
        'cmake -G "Unix Makefiles" ' +
        '-DCMAKE_CXX_FLAGS="{}" '.format(tc.CXXFLAGS) +
        '-DCMAKE_CXX_COMPILER={} '.format(tc.CXX) +
#        '-DCMAKE_CXX_LINK_FLAGS="-Wl,-rpath,${GCC_HOME}/lib64 -L${GCC_HOME}/lib64" ' +
        '-DLLVM_ENABLE_TERMINFO="OFF" ' +
        '-DCMAKE_C_COMPILER={} '.format(tc.CC) +
        '-DCMAKE_C_FLAGS="{}" '.format(tc.CFLAGS) +
        '-DCMAKE_BUILD_TYPE=Debug ' +
        '-DCMAKE_INSTALL_PREFIX="/chroma/src/install/llvm6-nvptx" ' +
        '-DLLVM_TARGETS_TO_BUILD="X86;NVPTX" ' +
        '-DLLVM_ENABLE_ZLIB="OFF" ' +
        '-DBUILD_SHARED_LIBS="ON" ' +
        '-DLLVM_ENABLE_RTTI="ON" ' +
        '/chroma/src/llvm6-trunk',
        'make -j4',
        'make install']
Stage0 += shell(commands=llvm)

# QMP
qmp_cm = hpccm.ConfigureMake(opts=['--with-qmp-comms-type=MPI'],
                             prefix='/chroma/install/qmp')
qmp = [git.clone_step(
    repository='https://github.com/usqcd-software/qmp',
    commit='6c92e769e956034d8b1dd8c6b2e0507f9236dfaf', path='/chroma/src'),
       'cd /chroma/src/qmp',
       'autoreconf -fiv',
       qmp_cm.configure_step(directory='/chroma/src/qmp', toolchain=mpi_tc),
       qmp_cm.build_step(),
       qmp_cm.install_step()]
Stage0 += shell(commands=qmp)

# QDP++
qdpxx_cm = hpccm.ConfigureMake(
    opts=['--with-libxml2',
          '--with-qmp=/chroma/install/qmp',
          '--enable-comm-split-deviceinit',
          '--enable-parallel-arch=parscalar',
          '--enable-precision=double',
          '--enable-largefile',
          '--enable-parallel-io',
          '--enable-dml-output-buffering',
          '--disable-generics',
          '--disable-filedb',
          '--with-cuda={}'.format(mpi_tc.CUDA_HOME),
          '--with-llvm=/chroma/install/llvm6-nvptx',
          '--enable-llvm6-trunk'],
    prefix='/chroma/install/qdpxx')
qdpxx = [git.clone_step(
    repository='https://github.com/usqcd-software/qdpxx', 
    commit='cd90bc9f9bed34ba19b9f3a3747f965dc6b42e4e', path='/chroma/src'),
         'cd /chroma/src/qdpxx',
         'autoreconf -fiv',
         qdpxx_cm.configure_step(directory='/chroma/src/qdpxx',
                                 toolchain=mpi_tc),
         qdpxx_cm.build_step(),
         qdpxx_cm.install_step()]
Stage0 += shell(commands=qdpxx)

# Eigen
eigen = [git.clone_step(
    repository='https://github.com/eigenteam/eigen-git-mirror',
    branch='3.3.4', directory='eigen-3.3.4', path='/chroma/src')]
Stage0 += shell(commands=eigen)

# QUDA
quda = [git.clone_step(
    repository='https://github.com/lattice/quda',
    commit='8ec0f1b7ddfac06af5a3de5683613656a6bbc2a6', path='/chroma/src'),
        'mkdir -p /chroma/build/quda',
        'cd /chroma/build/quda',
#        'cd /chroma/src/quda',
#        'autoreconf -fiv',
        'cmake ' +
        '-DQUDA_BUILD_ALL_TESTS=OFF ' +
        '-DQUDA_DIRAC_CLOVER=ON ' +
        '-DQUDA_DIRAC_DOMAIN_WALL=OFF ' +
        '-DQUDA_DIRAC_NDEG_TWISTED_MASS=OFF ' +
        '-DQUDA_DIRAC_STAGGERED=OFF ' +
        '-DQUDA_DIRAC_TWISTED_MASS=OFF ' +
        '-DQUDA_DIRAC_TWISTED_CLOVER=OFF ' +
        '-DQUDA_DIRAC_WILSON=ON ' +
        '-DQUDA_DYNAMIC_CLOVER=OFF ' +
        '-DQUDA_FORCE_ASQTAD=OFF ' +
        '-DQUDA_FORCE_GAUGE=OFF ' +
        '-DQUDA_FORCE_HISQ=OFF ' +
        '-DQUDA_GAUGE_ALG=OFF ' +
        '-DQUDA_GAUGE_TOOLS=OFF ' +
        '-DQUDA_GPU_ARCH={} '.format(sm_target) +
#        '-DQUDA_INTERFACE_QDPJIT=ON ' +
#        '-DQUDA_QDPJIT=ON ' +
#        '-DQUDA_QDPJITHOME=${INSTALLDIR}/qdp++-double ' +
        '-DQUDA_INTERFACE_MILC=OFF ' +
        '-DQUDA_INTERFACE_CPS=OFF ' +
        '-DQUDA_INTERFACE_QDP=ON ' +
        '-DQUDA_INTERFACE_TIFR=OFF ' +
        '-DQUDA_MAGMA=OFF ' +
        '-DQUDA_QMP=ON ' +
        '-DQUDA_OPENMP=ON ' +
        '-DQUDA_QMPHOME=/chroma/install/qmp ' +
        '-DQUDA_MULTIGRID=ON ' +
        '-DQUDA_DOWNLOAD_EIGEN=NO ' +
        '-DEIGEN_INCLUDE_DIR=/chroma/src/eigen-3.3.4 ' +
        '-DCMAKE_INSTALL_PREFIX=/chroma/install/quda ' +
        '-DCMAKE_BUILD_TYPE=DEVEL ' +
        '-DCMAKE_CXX_COMPILER={} '.format(mpi_tc.CXX) +
        '-DCMAKE_C_COMPILER={} '.format(mpi_tc.CC) +
        '-DCMAKE_LINKER={} '.format(mpi_tc.CXX) +
#        '-DCMAKE_EXE_LINKER_FLAGS="${OMPFLAGS} -L${LLVM_INSTALL_DIR}/lib"' +
        '-DCMAKE_EXE_LINKER_FLAGS="-fopenmp -D_REENTRANT" ' +
        '/chroma/src/quda',
        'make -j4',
        'make install']
Stage0 += shell(commands=quda)

chroma_cm = hpccm.ConfigureMake(
    opts=['--with-qmp=/chroma/install/qmp',
#          '--with-qdp=/chroma/install/qdp',
          '--with-quda=/chroma/install/quda',
          '--with-cuda={}'.format(mpi_tc.CUDA_HOME),
          '--enable-cpp-wilson-dslash',
          '--enable-c-scalarsite-bicgstab-kernels'],
    prefix='/chroma/install/chroma')
chroma = [git.clone_step(
    repository='https://github.com/JeffersonLab/chroma',
    commit='33d924f71c9612f0793d4053572bc2c47ff52aeb', path='/chroma/src'),
          'cd /chroma/src/chroma',
          'autoreconf -fiv',
          chroma_cm.configure_step(directory='/chroma/src/chroma',
                                   toolchain=mpi_tc),
          chroma_cm.build_step(),
          chroma_cm.install_step()]
Stage0 += shell(commands=chroma)          

#checkout.append(git.clone_step(
#    repository='https://github.com/fwinter/qdp-jit',
#    commit='a53175b63af4ce0d06d3383fa41682d1f9b5fcc0',
#    directory='qdp-jit-llvm-nvptx', path='/chroma/src'))
#Stage0 += shell(commands=checkout)
