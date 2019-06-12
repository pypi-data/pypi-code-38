from human_body_prior.tools.model_loader import load_vposer
import torch
from human_body_prior.tools.omni_tools import makepath, id_generator
import os
from human_body_prior.body_model.body_model import BodyModel
from human_body_prior.mesh import MeshViewer
from human_body_prior.tools.omni_tools import copy2cpu as c2c
import trimesh
from human_body_prior.tools.omni_tools import colors
from human_body_prior.tools.omni_tools import apply_mesh_tranfsormations_

from human_body_prior.tools.visualization_tools import imagearray2file
import numpy as np

def save_testset_samples(vposer_model, ps, batch_size=5, save_upto_bnum=10):
    comp_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    vposer_model.eval()
    vposer_model = vposer_model.to(comp_device)

    view_angles = [0, 180, 90, -90]
    imw, imh = 800, 800

    mv = MeshViewer(width=imw, height=imh, use_offscreen=True)
    mv.render_wireframe = True

    bm_path = '/ps/project/common/moshpp/smplh/locked_head/neutral/model.npz'
    bm = BodyModel(bm_path, 'smplh', batch_size=1, use_posedirs=True).to(comp_device)

    images_gen = np.zeros([len(view_angles), batch_size, 1, imw, imh, 3])

    test_savepath = os.path.join(ps.work_dir, 'evaluations', 'testset_samples', os.path.basename(ps.best_model_fname).replace('.pt',''))
    for bId in range(save_upto_bnum):

        imgpath = makepath(os.path.join(test_savepath, '%s.png' % (id_generator(5))), isfile=True)
        pgen_aa = vposer_model.sample_poses(batch_size).contiguous().view(batch_size, -1)

        for cId in range(batch_size):
            bm.pose_body.data[:] = bm.pose_body.new(pgen_aa[cId])
            gen_body_mesh = trimesh.Trimesh(vertices=c2c(bm().v[0]), faces=c2c(bm.f), vertex_colors=np.tile(colors['blue'], (6890, 1)))
            for rId, angle in enumerate(view_angles):
                if angle != 0: apply_mesh_tranfsormations_([gen_body_mesh], trimesh.transformations.rotation_matrix(np.radians(angle),
                                                                                                   (0, 1, 0)))
                mv.set_meshes([gen_body_mesh], group_name='static')
                images_gen[rId, cId, 0] = mv.render()

                if angle != 0: apply_mesh_tranfsormations_([gen_body_mesh],
                                                           trimesh.transformations.rotation_matrix(np.radians(-angle),
                                                                                                   (0, 1, 0)))

        imagearray2file(images_gen, imgpath.replace('.png', '_gen.png'))


if __name__ == '__main__':
    dataset_dir= '/ps/project/humanbodyprior/VPoser/data/004_00_amass/smpl/pytorch/final_dsdir'
    expr_basedir = '/ps/project/humanbodyprior/VPoser/smpl/pytorch'

    # for ds_name in ['amass', 'CMU','EKUT', 'MPI_Limits', 'TotalCapture', 'Eyes_Japan_Dataset', 'ACCAD', 'KIT','BML','TCD_handMocap']:
    #     for prex in ['', '_WO']:
    #         expr_code = '004_00' + prex + '_%s'%ds_name.lower()
    #         expr_dir = os.path.join(expr_basedir, expr_code)
    #         if not os.path.exists(expr_dir):
    #             print('%s does not exist'%expr_dir)
    #             continue
    #
    #         vposer_model, vposer_ps = load_vposer(expr_dir, model_type='smpl', use_snapshot_model = True)
    #
    #         save_testset_samples(dataset_dir, vposer_model, vposer_ps, batch_size=5, save_upto_bnum=10)
    #         v2v_mae = evaluate_test_error(dataset_dir, vposer_model, vposer_ps, batch_size=512)
    #         print('[%s] v2v_mae = %.2e' % (vposer_ps.best_model_fname, v2v_mae))

    expr_dir = '/ps/project/common/vposer/smpl/0020_0700R10_T2'
    vposer_model, vposer_ps = load_vposer(expr_dir, vp_model='snapshot')
    save_testset_samples(vposer_model, vposer_ps, batch_size=5, save_upto_bnum=10)