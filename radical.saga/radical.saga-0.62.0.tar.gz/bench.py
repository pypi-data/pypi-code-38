
import time

import radical.saga as rs


num_jobs = [0, 0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
backends = [#'slurm+ssh://tg803521@stampede.tacc.utexas.edu',
                   'ssh://tg803521@stampede.tacc.utexas.edu',
                   'ssh://localhost']


with open ('./output.dat.ssh', 'a') as of :
    import subprocess as sp
    for num in num_jobs :
    
        start = time.time ()
        for i in range (num) :
            try :
                p = sp.Popen ('ssh localhost /bin/true',
                                stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
                out = p.communicate()[0]
            except Exception as e :
                print e


        stop = time.time ()
      
        print     "%30s  %-5d : %4.1f"   % ('ssh-localhost', num, stop-start)
        of.write ("%30s  %-5d : %4.1f\n" % ('ssh localhost', num, stop-start))


# with open ('./output.dat', 'a') as of :
# 
#   for backend in backends :
#   
#       for num in num_jobs :
#   
#           start = time.time ()
#           js    = rs.job.Service (backend)
#           jd    = rs.job.Description ()
# 
#           jd.executable      = '/bin/true'
#         # jd.queue           = 'normal'
#         # jd.wall_time_limit = 1
#   
#           for n in range (num) :
#   
#               j = js.create_job (jd)
#               j.run ()
#               pass
#   
#           stop = time.time ()
#   
#           print     "%30s  %-5d : %4.1f"   % (backend, num, stop-start)
#           of.write ("%30s  %-5d : %4.1f\n" % (backend, num, stop-start))


