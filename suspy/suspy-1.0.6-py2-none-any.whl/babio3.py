import dmft 
import h5py
import impurity_green_function as igf
import numpy as np
import fft
import tqdm
import os
import datetime
import xi_tools 
import itertools as it
import holstein as h
import suspy

from pyed.SparseExactDiagonalization import SparseExactDiagonalization



def run(mc, n_max, num_iw, num_iw_xi, n_tau, nloops, Ud, mu, t1, t2, t4, beta, gamma_bd, eb, tot, delta, file_name='data', to_compute=['gf', 'xi']):
    
    Vcd = ec = 0
    wn = np.pi / beta * (2 * np.arange(0, num_iw//2) + 1)
    wn_xi = np.pi / beta * (2 * np.arange(-num_iw_xi//2, num_iw_xi//2) + 1)

    tau = np.linspace(0, beta, n_tau)
    dt = np.ones(n_tau) * tau[1]
    dt[0] = dt[-1] = tau[1]/2.

    print '-' * 20 + '***' + "-" * 20
    print '\nStart DMFT loop {0}\n'.format(datetime.datetime.now())
    print '-' * 20 + '***' + "-" * 20
    print '\n\n'

    sq = dmft.Square((t1, t2, t4), mc, n_max, Ud, beta, num_iw, Vcd, gamma_bd , ec, eb, mu=0, delta=delta)
    g0 = igf.g_imp(t1, t2, t4, wn, num_iw//2, mu=mu)
    sq.main_loop(nloops, mu, g0, tot)

    ops = [[sq.c_dag_up(), sq.c_up()], [sq.c_dag_down(), sq.c_down()]]#, [H.c_dag_up(), H.c_down()], [H.c_dag_down(), H.c_up()]]
    all_ops = [ i[0] + i[1] for i in it.product(ops, repeat=2)]

    path = './suspy_computation/'
    print '-' * 20 + '***' + "-" * 20
    if not os.path.exists(path):
        os.mkdir(path)
        print '\nCreate a directory {0}\n'.format(path)
    else:
        print "\nDirectory {0} exists\n".format(path)
    _file = h5py.File(path + file_name, 'a')
    print '-' * 20 + '***' + "-" * 20
    print '\n\n'

    print '-' * 20 + '***' + "-" * 20
    print '\nSaving Green Function and parameters in {0} at {1}\n'.format(path, datetime.datetime.now())
    _file.create_dataset('fit_error', data=sq.all_tot)
    _file.create_dataset('gf', data=sq.get_g())
    _file.create_dataset('Vcd', data=sq.Vcd)
    _file.create_dataset('ec', data=sq.ec)
    print '-' * 20 + '***' + "-" * 20
    print '\n\n'

   
    
    if 'xi' in to_compute:
        print '-' * 20 + '***' + "-" * 20
        print "\nStart xi computation {0}\n".format(datetime.datetime.now())
        print '-' * 20 + '***' + "-" * 20
        print '\n\n'
        for step in range(len(all_ops))[:2]:

            xi = np.zeros((num_iw_xi, num_iw_xi), dtype=np.complex64)
            g2_tau1, g2_tau2, g4_tau = xi_tools.init_gfs(sq.ed, n_tau, sq.beta, all_ops[step])
            g2_1, g2_2, g4 = g2_tau1.data[:, 0, 0], g2_tau2.data[:, 0, 0], g4_tau.data[:, :, :, 0, 0, 0, 0]
            xi_tools.xi_mats(xi, g2_1, g2_2, g4, wn_xi, tau, dt)
            #xi_tools.xi_sc_iter(xi, g4, wn_xi, tau, dt)

            print '-' * 20 + '***' + "-" * 20
            print '\nSaving xi_{0}_{1} at {2}\n'.format(step, int(sq.beta), datetime.datetime.now())
            _file.create_dataset('xi_{}'.format(step), data=xi)
            print '-' * 20 + '***' + "-" * 20
            print '\n\n'

    print "Calculation finished {0}\n\n".format(datetime.datetime.now())

def main(*args):
    to_compute = [arg.lower().strip() for arg in args]
#     return to_compute
    a = ''
    n = 'input_data.txt'

    if not os.path.exists('./' + n):
        os.system('cp -rf {0}/{2} {1}/{2}'.format(os.path.dirname(suspy.__file__), os.getcwd(), n))

    f = open(os.getcwd() + '/' + n, 'r')
    params = [float(i.split('=')[1].split()[0]) if '.' in i.split('=')[1].split()[0] else int(i.split('=')[1].split()[0]) for i in f]
    mc, n_max, num_iw, num_iw_xi, n_tau, nloops, Ud, mu, t1, t2, t4, beta, gamma_bd, eb, tot, delta = params
    file_name = 'output_{0}_{1}_{2}_{3}'.format(mc, n_max, int(beta), n_tau)
    print '-' * 20 + '***' + "-" * 20
    print '\nInitial parameters\n'
    print 'mc = {}\nn_max = {}\nU = {}\nmu={}\nt={}\nbeta={}\nnum_iw={}\ngamma_bd={}\nw0={}\nn_tau={}\n'.format(
            mc, n_max, Ud, mu, [t1, t2, t4], beta, [num_iw, num_iw_xi], gamma_bd, eb, n_tau)
    print 'Output file: {}\n'.format(file_name)
    print '-' * 20 + '***' + "-" * 20
    print '\n\n'
    
    run(mc, n_max, num_iw, num_iw_xi, n_tau, nloops, Ud, mu, t1, t2, t4, beta, gamma_bd, eb, tot, delta, file_name, to_compute)