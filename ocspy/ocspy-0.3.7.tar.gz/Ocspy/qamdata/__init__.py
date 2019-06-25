# from ..ReceiverDsp.dsp_tools import cal_symbols_qam
# from ..ReceiverDsp.dsp_tools import cal_scaling_factor_qam
#

# # import numpy as np
# # QPSK = cal_symbols_qam(4)/np.sqrt(cal_scaling_factor_qam((4)))
# #
# #



import os
names = os.listdir('./*.mat')
if not names:
    names = os.listdir('./')
    for name in names:
        if 'qam' in name and name.endswith('py'):

            os.rename(name,f'{name.split(".")[0]}.mat')






