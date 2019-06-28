# from ..ReceiverDsp.dsp_tools import cal_symbols_qam
# from ..ReceiverDsp.dsp_tools import cal_scaling_factor_qam
#

# # import numpy as np
# # QPSK = cal_symbols_qam(4)/np.sqrt(cal_scaling_factor_qam((4)))
# #
# #


# from ..ReceiverDsp.dsp_tools import cal_symbols_qam
# from ..ReceiverDsp.dsp_tools import cal_scaling_factor_qam
#

# # import numpy as np
# # QPSK = cal_symbols_qam(4)/np.sqrt(cal_scaling_factor_qam((4)))
# #
# #



import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))+'/'

names = os.listdir(BASE_DIR)

# znames = os.listdir('./')
for name in names:
    if name.endswith('.mat'):
        flag=True
        break

else:
    flag = False


if not flag:
    for name in names:
        if 'qam' in name and name.endswith('py'):

            os.rename(BASE_DIR+name,BASE_DIR+f'{name.split(".")[0]}.mat')


if flag:
    for name in names:
        if 'qam' in name and '.py' in name:
            os.remove(BASE_DIR+name)




