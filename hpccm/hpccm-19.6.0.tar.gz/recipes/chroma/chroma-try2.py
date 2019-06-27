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

# Mellanox OFED
mofed = mlnx_ofed()
Stage0 += mofed

# MVAPICH 2.3b
mv2 = mvapich2(configure_opts=['--disable-fortran', '--disable-mcast'],
               prefix='/mvapich/install', version='2.3b')
Stage0 += mv2

# Temporary hack to get the MPI compilers working
Stage0 += environment(variables={'LD_LIBRARY_PATH': '$LD_LIBRARY_PATH:/usr/lib/x86_64-linux-gnu:/usr/local/cuda/lib64/stubs'})
Stage0 += shell(commands=['ln -s /usr/local/cuda/lib64/stubs/libnvidia-ml.so /usr/local/cuda/lib64/stubs/libnvidia-ml.so.1'])

Stage0 += apt_get(ospackages=['autoconf', 'automake', 'ca-certificates',
                              'cmake', 'flex', 'git', 'libtool', 'libxml2-dev',
                              'm4', 'pkg-config', 'python', 'vim-common'])

# Copy build scripts
Stage0 += copy(src='recipes/chroma/jit-llvm-nvptx',
               dest='/chroma/jit-llvm-nvptx')

# Checkout Chroma and all its dependencies
git_config = 'git config --global url.https://github.com/.insteadOf git@github.com:'
git = hpccm.git(opts=['--recursive'])
checkout = [
    git.clone_step(repository='https://github.com/JeffersonLab/chroma',
                   commit='33d924f71c9612f0793d4053572bc2c47ff52aeb',
                   path='/chroma/src'),
    git.clone_step(repository='https://github.com/eigenteam/eigen-git-mirror',
                   branch='3.3.4', directory='eigen-3.3.4',
                   path='/chroma/src'),
    git.clone_step(repository='https://github.com/llvm-mirror/llvm',
                   commit='dbbb6c5fc3642987430866dffdf710df4f616ac7',
                   directory='llvm6-trunk', path='/chroma/src'),
    git.clone_step(repository='https://github.com/fwinter/qdp-jit',
                   commit='a53175b63af4ce0d06d3383fa41682d1f9b5fcc0',
                   directory='qdp-jit-llvm-nvptx', path='/chroma/src'),
    git.clone_step(repository='https://github.com/usqcd-software/qdpxx', 
                   commit='cd90bc9f9bed34ba19b9f3a3747f965dc6b42e4e',
                   path='/chroma/src'),
    git.clone_step(repository='https://github.com/usqcd-software/qmp',
                   commit='6c92e769e956034d8b1dd8c6b2e0507f9236dfaf',
                   path='/chroma/src'),
    git.clone_step(repository='https://github.com/lattice/quda',
                   commit='8ec0f1b7ddfac06af5a3de5683613656a6bbc2a6',
                   path='/chroma/src')
]

autoreconf = [
    'cd /chroma/src/chroma', 'autoreconf -fiv',
    'cd /chroma/src/qdp-jit-llvm-nvptx', 'autoreconf -fiv',
    'cd /chroma/src/qdpxx', 'autoreconf -fiv',
    'cd /chroma/src/qmp', 'autoreconf -fiv',
    'cd /chroma/src/quda', 'autoreconf -fiv'
]

build = [
    'cd /chroma/jit-llvm-nvptx',
    'QDPXX_CONFIG=/chroma/jit-llvm-nvptx/build/build_qdp++-double/qdp++-config ./build_all.sh'
]

chroma = []
chroma.append(git_config)
chroma.extend(checkout)
chroma.extend(autoreconf)
#chroma.extend(build)

Stage0 += shell(commands=chroma)

Stage0 += shell(commands=[
    'cd /chroma/jit-llvm-nvptx',
    'QDPXX_CONFIG=/chroma/jit-llvm-nvptx/build/build_qdp++-double/qdp++-config ./build_llvm_trunk.sh'
])

Stage0 += shell(commands=[
    'cd /chroma/jit-llvm-nvptx',
    'QDPXX_CONFIG=/chroma/jit-llvm-nvptx/build/build_qdp++-double/qdp++-config ./build_qmp.sh'
])

Stage0 += shell(commands=[
    'cd /chroma/jit-llvm-nvptx',
    'QDPXX_CONFIG=/chroma/jit-llvm-nvptx/build/build_qdp++-double/qdp++-config ./build_qdp++-double.sh'
])

Stage0 += shell(commands=[
    'cd /chroma/jit-llvm-nvptx',
    'QDPXX_CONFIG=/chroma/jit-llvm-nvptx/build/build_qdp++-double/qdp++-config SM_TARGET={} ./build_quda_qdp_double-cmake.sh'.format(sm_target),
    'chmod 755 /chroma/jit-llvm-nvptx/build/build_qdp++-double/qdp++-config'
])

Stage0 += shell(commands=[
    'cd /chroma/jit-llvm-nvptx',
    'QDPXX_CONFIG=/chroma/jit-llvm-nvptx/build/build_qdp++-double/qdp++-config ./build_chroma-double.sh'
])
