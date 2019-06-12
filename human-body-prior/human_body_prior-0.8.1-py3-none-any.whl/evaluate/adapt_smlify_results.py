import pickle as pickle
import glob
import os
from human_body_prior.tools.omni_tools import makepath

results_path = '/ps/project/humanbodyprior/VPoser/smpl/pytorch/004_00_amass/evaluations/smplifypp/TR00_E092/results_py3'
out_path = '/ps/project/humanbodyprior/VPoser/smpl/pytorch/004_00_amass/evaluations/smplifypp/TR00_E092/results'
pkls = glob.glob(os.path.join(results_path,'*/*.pkl'))

for pkl in pkls:
    with open(pkl, 'rb') as f:
        data = pickle.load(f)
    out_pkl = os.path.join(out_path, '/'.join(pkl.split('/')[-2:]))
    print(out_pkl)
    with open(makepath(out_pkl, isfile=True), 'wb') as f:
        pickle.dump(data, f, protocol=2)