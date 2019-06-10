import nibabel as nib
import numpy as np


def unc_to_nifti(unc, flip_lr=False):
    pix, aff = dcm_affine(unc, flip_lr=flip_lr)
    nii = nib.Nifti1Image(pix, aff)
    nii.header.set_xyzt_units(xyz='mm')
    nii.set_qform(aff, 1, update_affine=True)
    nii.set_sform(np.eye(4), code=0)
    nii.update_header()
    return nii


def dcm_affine(unc, flip_lr=False):
    iop = unc.header.image_orientation_patient_coordinates
    F = np.array(
        [[iop[0], iop[3]],
         [iop[1], iop[4]],
         [iop[2], iop[5]]]
    )
    dr = float(unc.header.pixel_x_size)
    dc = float(unc.header.pixel_y_size)
    T1 = np.array([unc.header.slices[0].image_position_patient]).T
    Tn = np.array([unc.header.slices[-1].image_position_patient]).T
    k = (T1 - Tn) / (1 - len(unc.header.slices))

    R = np.eye(4, 4)
    R[0:3, 0] = F[:, 0] * dr
    R[0:3, 1] = F[:, 1] * dc
    R[0:3, 2] = k[:, 0]
    R[0:3, 3] = T1[:, 0]

    absR = np.abs(R[0:3, 0:3])
    ixyz = np.argmax(absR[0:3, 0:3], axis=0)
    if ixyz[1] == ixyz[0]:
        absR[ixyz[1], 1] = 0
        ixyz[1] = np.argmax(ixyz[:, 1])
    if np.any(ixyz[2] == ixyz[0:2]):
        ixyz[2] = np.setdiff1d(np.array(range(0, 2)), ixyz[1:3])

    # convert LPS to RAS
    R[0:2, :] *= -1.0

    perm = np.argsort(ixyz)
    acq_3d = unc.header.dicom.get('MR Acquisition Type', '') == '3D'
    axes_sorted = np.all(np.equal(np.array(range(3)), perm))
    if acq_3d and not axes_sorted:
        pixels = unc.pixels.T
        pixels = np.flip(pixels, axis=2)
        R[:, 0:3] = R[:, perm]
        ixyz = ixyz[perm]
        pixels = np.transpose(pixels, perm)
    else:
        pixels = np.flip(unc.pixels.T, 1)
        pixels = np.rot90(pixels, k=2, axes=(0, 2))
        pixels = np.rot90(pixels, k=2, axes=(0, 1))

    ind4 = ixyz + np.array([0, 4, 8])
    flp = np.zeros(3)
    flp[R.flatten(order='F')[ind4] < 0] = 1
    d = np.linalg.det(R[0:3, 0:3]) * np.prod(1 - flp * 2)
    if d > 0:
        if flp[0] == 1:
            flp[0] = 0
        else:
            flp[1] = 1
    diag_arg = np.concatenate(((1 - flp * 2), np.array([1])))
    rotM = np.diag(diag_arg)
    rotM[0:3, 3] = (np.array(unc.dimv[3:0:-1]) - 1) * flp
    R = np.dot(R, np.linalg.inv(rotM))
    pixels = np.rot90(pixels, k=2, axes=(0, 2))
    pixels = np.rot90(pixels, k=2, axes=(0, 1))
    if flip_lr:
        if flp[1] == 1:
            flip_axis = 2
        else:
            flip_axis = 0
        pixels = np.flip(pixels, axis=flip_axis)
    return pixels, R
