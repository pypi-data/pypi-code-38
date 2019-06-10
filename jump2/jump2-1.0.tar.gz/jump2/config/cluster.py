#==/name/quene/nodes/cores/walltime/enviroment/==
class Cluster(object):
    __manager__={
    "bash":{"head":"""\
#!/bin/bash
# name  = {0}
# queue = {1}
# nodes = {2}
# cores = {3}
# wlltm = {4}
WORKDIR=$(pwd)
# log on compute-node % 
ssh {2} 
cd $WORKDIR
touch .running
# parellel environment % 
P_ENV={5}
export OMP_NUM_THREADS=1 
export PATH=$P_ENV/bin:$PATH
export LD_INCLCUDE_PATH=$P_ENV/include:$LD_INCLUDE_PATH
export LD_LIBRARY_PATH=$P_ENV/lib:$LD_LIBRARY_PATH

""",
"cmd":{'submit':'source pbsscript.pbs', 'del':'kill -9 '}},

'sge':{"head":"""\
#!/bin/bash 
#$ -S /bin/bash 
#$ -V 
#$ -N {0} 
#$ -pe {3} {2} 
#$ -j y
#$ -o .running
#$ -cwd
#$ -e .error

if [ -f ".wait" ]; then
rm .wait
fi 

source /share/apps/pylada/pylada_env.sh 
# parellel environment % 
P_ENV={5}
export OMP_NUM_THREADS=1 
export PATH=$P_ENV/bin:$PATH
export LD_INCLCUDE_PATH=$P_ENV/include:$LD_INCLUDE_PATH
export LD_LIBRARY_PATH=$P_ENV/lib:$LD_LIBRARY_PATH

""",
"cmd": {'submit':'qsub pbsscript', 'del':'qdel '}},
'pbs':{"head":"""\
#!/bin/bash
#PBS -N {0}
#PBS -S /bin/bash
#PBS -r n
#PBS -l nodes={1}:ppn={2}
#PBS -q {3}
#PBS -l walltime={4}
#PBS -j oe
#PBS -o .running 
#PBS -V

# go to work dir % 
cd $PBS_O_WORKDIR

# parellel environment % 
P_ENV={5}
export PATH=~/.jump2/bin:$PATH
export OMP_NUM_THREADS=1 
export PATH=$P_ENV/bin:$PATH
export LD_INCLCUDE_PATH=$P_ENV/include:$LD_INCLUDE_PATH
export LD_LIBRARY_PATH=$P_ENV/lib:$LD_LIBRARY_PATH

""",
"cmd": {'submit':'qsub pbsscript', 'del': 'qdel '}},
'slurm':{"head":"""\
""",
"cmd":{'submit':None, 'del':None}},
'lsf':{"head":"""\
#!/bin/sh
#BSUB -J {0}
#BSUB -o .running 
#BSUB -n {1}
#BSUB -R "span[ptile={2}]" 
#BSUB -q {3}
#BSUB -W {4}

# parellel environment %
P_ENV={5}
export OMP_NUM_THREADS=1 
export PATH=$P_ENV/bin:$PATH
export LD_INCLCUDE_PATH=$P_ENV/include:$LD_INCLUDE_PATH
export LD_LIBRARY_PATH=$P_ENV/lib:$LD_LIBRARY_PATH

""",
"cmd":{'submit':'bsub < pbsscript', 'del': 'bkill '}}
}

    ppath=None
    nodes=1
    cores=20
    queue='impi2'
    walltime="600:00:00"
    mpi_env='/opt/openmpi-1.8.4/'
    manager='sge'
    max_jobs=10

    def __init__(self, **kwargs):
        from os import path 
        import json

        # get default setting % 
        jpath = path.join(path.expanduser('~'), '.jump2/env/cluster_config.sh')
        if path.exists(jpath):
            with open(jpath, 'r') as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith('#'): continue 
                if 'potential' in line.split('=')[0]:
                    self.ppath=path.dirname(line.split('=')[1].strip())
                
                if 'mpi_env' in line.split('=')[0]:
                    self.mpi_env=path.dirname(line.split('=')[1].strip())
                
                if 'manager' in line.split('=')[0]:
                    self.manager=line.split('=')[1].strip()
                        
                if 'default_parallel' in line.split('=')[0]:
                    cluster=json.loads(line.split('=')[1])
                    cluster.update(kwargs)  # update cluster info % 
                    if cluster.has_key('nodes'):
                        self.nodes = cluster['nodes']
                    if cluster.has_key('cores'):
                        self.cores = cluster['cores']
                    if cluster.has_key('walltime'):
                        self.walltime = cluster['walltime']
                    if cluster.has_key('queue'):
                        self.queue = cluster['queue']
        else:
            raise IOError ("Please set the default in ~/.jump2cluster")

    @property
    def scripts(self):
        manager = self.__manager__[self.manager]
        if self.manager is 'sge':
            manager['head'] = manager['head'].format('{0}', self.nodes, 
                                                            self.nodes*self.cores,
                                                            self.queue,
                                                            self.walltime,
                                                            self.mpi_env)
                                
        elif self.manager is 'lsf':
            manager['head'] = manager['head'].format('{0}', self.nodes*self.cores, 
                                                            self.cores,
                                                            self.queue,
                                                            self.walltime,
                                                            self.mpi_env)
                                
        else:
            manager['head'] = manager['head'].format('{0}', self.nodes, 
                                                            self.cores,
                                                            self.queue,
                                                            self.walltime,
                                                            self.mpi_env)
        return manager                         

    @property
    def potential_path(self):
        return self.ppath
   #@property 
   #def nodes(self, value=1):
   #    return int(value)

   #@property
   #def codes(self, value=16):
   #    return int(value)

   #@property
   #def queue(self, value=None):
   #    return str(value)

   #@property
   #def walltime(self, value='600:00:00'):
   #    return str(value)

   #@property
   #def mpirun(self, value=None):
   #    return str(value)

   #@property
   #def max_jobs(self, value=10):
   #    return value

   #@property
   #def manager(self, value='bash'):
   #    return value

