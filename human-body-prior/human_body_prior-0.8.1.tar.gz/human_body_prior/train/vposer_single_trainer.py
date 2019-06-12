from human_body_prior.train.vposer_smpl import run_vposer_trainer
from configer import Configer

expr_code = '004_02_WO_accad'
args = {
    'expr_code' : expr_code,
    'base_lr': 0.005,

    'dataset_dir': '/ps/project/humanbodyprior/VPoser/data/005_00_WO_accad/smpl/pytorch/stage_III',
    'work_dir': '/ps/project/humanbodyprior/VPoser/smpl/pytorch/%s'%expr_code,
}
ps = Configer(default_ps_fname='./vposer_smpl_defaults.ini', **args)

# expr_message = '\n[%s] %d H neurons, latentD=%d, batch_size=%d, kl_coef = %.1e\n' \
#                % (ps.expr_code, ps.num_neurons, ps.latentD, ps.batch_size, ps.kl_coef)
# expr_message += 'Trained on all of AMASS except ACCAD\n'
# expr_message += 'Pose reconstruction loss L2 on matrix-rotation representation\n'
# expr_message += 'Using Batch Normalization\n'
# expr_message += '\n'
# ps.expr_message = '''%s'''%expr_message
expr_message = '\n[%s] %d H neurons, latentD=%d, batch_size=%d,  kl_coef = %.1e\n' \
               % (ps.expr_code, ps.num_neurons, ps.latentD, ps.batch_size, ps.kl_coef)
expr_message += 'Trained on all of amass excpet accad\n'
expr_message += 'Using SMPL to produce meshes of the bodies\n'
expr_message += 'Reconstruction loss is L1 on meshes\n'
expr_message += 'Using Batch Normalization\n'
expr_message += '\n'
ps.expr_message = expr_message
run_vposer_trainer(ps)