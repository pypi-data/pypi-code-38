"""Implementation of the  method."""

import cv2
import numpy as np
import scipy.ndimage
import sys
import time
from .. import extrapolation
from .. import cascade
from .. import noise
from ..postprocessing import probmatching
from sklearn.decomposition import PCA
from ..timeseries import autoregression, correlation

try:
    import dask

    dask_imported = True
except ImportError:
    dask_imported = False


class BayesianNowcasting:
    def __init__(
        self,
        X,
        V,
        n_ens_members,
        n_cascade_levels,
        R_thr=None,
        R_min=None,
        wet_thr=0.5,
        expl_variance=0.999,
        kmperpixel=None,
        timestep=None,
        extrap_method="semilagrangian",
        decomp_method="fft",
        bandpass_filter_method="gaussian",
        noise_method="nonparametric",
        noise_stddev_adj=True,
        ar_order=2,
        vel_pert_method=None,
        conditional=False,
        use_precip_mask=True,
        use_probmatching=True,
        mask_method="incremental",
        callback=None,
        return_output=True,
        seed=None,
        num_workers=None,
        extrap_kwargs={},
        filter_kwargs={},
        noise_kwargs={},
        vel_pert_kwargs={},
    ):

        self._check_inputs(X, V, ar_order)

        if np.any(~np.isfinite(X)):
            raise ValueError("X contains non-finite values")

        if np.any(~np.isfinite(V)):
            raise ValueError("V contains non-finite values")

        if mask_method not in ["obs", "incremental"]:
            raise ValueError(
                "unknown mask method %s: must be 'obs' or 'incremental'" % mask_method
            )

        if conditional and R_thr is None:
            raise Exception("conditional=True but R_thr is not set")

        if use_probmatching and R_thr is None:
            raise Exception("use_probmatching=True but R_thr is not set")

        if kmperpixel is None:
            if vel_pert_method is None:
                raise Exception("vel_pert_method is set but kmperpixel=None")
            if mask_method == "incremental":
                raise Exception("mask_method='incremental' but kmperpixel=None")

        if timestep is None:
            if vel_pert_method is None:
                raise Exception("vel_pert_method is set but timestep=None")
            if mask_method == "incremental":
                raise Exception("mask_method='incremental' but timestep=None")

        print("Initializing Bayesian nowcast:")
        print("------------------------")
        print("")

        print("Inputs:")
        print("-------")
        print("input dimensions: %dx%d" % (X.shape[1], X.shape[2]))
        if kmperpixel is not None:
            print("km/pixel:         %g" % kmperpixel)
        if timestep is not None:
            print("time step:        %d minutes" % timestep)
        print("")

        print("Methods:")
        print("--------")
        print("extrapolation:          %s" % extrap_method)
        print("bandpass filter:        %s" % bandpass_filter_method)
        print("decomposition:          %s" % decomp_method)
        print("noise generator:        %s" % noise_method)
        print("noise adjustment:       %s" % ("yes" if noise_stddev_adj else "no"))
        print("velocity perturbator:   %s" % vel_pert_method)
        print("conditional statistics: %s" % ("yes" if conditional else "no"))
        print("precipitation mask:     %s" % ("yes" if use_precip_mask else "no"))
        print("mask method:            %s" % mask_method)
        print("probability matching:   %s" % ("yes" if use_probmatching else "no"))
        print("")

        print("Parameters:")
        print("-----------")
        print("ensemble size:            %d" % n_ens_members)
        print("number of cascade levels: %d" % n_cascade_levels)
        print("order of the AR(p) model: %d" % ar_order)
        if vel_pert_method is "bps":
            vp_par = vel_pert_kwargs.get(
                "p_pert_par", noise.motion.get_default_params_bps_par()
            )
            vp_perp = vel_pert_kwargs.get(
                "p_pert_perp", noise.motion.get_default_params_bps_perp()
            )
            print(
                "velocity perturbations, parallel:      %g,%g,%g"
                % (vp_par[0], vp_par[1], vp_par[2])
            )
            print(
                "velocity perturbations, perpendicular: %g,%g,%g"
                % (vp_perp[0], vp_perp[1], vp_perp[2])
            )

        if conditional or use_probmatching:
            print("conditional precip. intensity threshold: %g" % R_thr)

        M, N = X.shape[1:]
        extrap_method = extrapolation.get_method(extrap_method)
        X = X[-(ar_order + 1) :, :, :].copy()

        if conditional or use_probmatching:
            MASK_thr = np.logical_and.reduce(
                [X[i, :, :] >= R_thr for i in range(X.shape[0])]
            )
        else:
            MASK_thr = None

        if R_min is None:
            R_min = X.min()

        # advect the previous precipitation fields to the same position with the
        # most recent one (i.e. transform them into the Lagrangian coordinates)
        extrap_kwargs = extrap_kwargs.copy()
        res = []
        f = lambda X, i: extrap_method(
            X[i, :, :], V, ar_order - i, R_min, **extrap_kwargs
        )[-1]
        for i in range(ar_order):
            if not dask_imported:
                X[i, :, :] = f(X, i)
            else:
                res.append(dask.delayed(f)(X, i))

        if dask_imported:
            X = np.stack(
                list(dask.compute(*res, num_workers=num_workers)) + [X[-1, :, :]]
            )

        # initialize the band-pass filter
        filter_method = cascade.get_method(bandpass_filter_method)
        filter = filter_method((M, N), n_cascade_levels, **filter_kwargs)

        # compute the cascade decompositions of the input precipitation fields
        decomp_method = cascade.get_method(decomp_method)
        X_d = []
        for i in range(ar_order + 1):
            X_ = decomp_method(X[i, :, :], filter, MASK=MASK_thr)
            X_d.append(X_)

        # normalize the cascades and rearrange them into a four-dimensional array
        # of shape (n_cascade_levels,ar_order+1,m,n) for the autoregressive model
        X_c, mu, sigma = self._stack_cascades(X_d, n_cascade_levels)
        X_d = None

        # compute lag-l temporal autocorrelation coefficients for each cascade level
        GAMMA = np.empty((n_cascade_levels, ar_order))
        for i in range(n_cascade_levels):
            X_c_ = np.stack([X_c[i, j, :, :] for j in range(ar_order + 1)])
            GAMMA[i, :] = correlation.temporal_autocorrelation(X_c_, MASK=MASK_thr)
        X_c_ = None
        X_c = None

        self._print_corrcoefs(GAMMA)

        if ar_order == 2:
            # adjust the lag-2 correlation coefficient to ensure that the AR(p)
            # process is stationary
            for i in range(n_cascade_levels):
                GAMMA[i, 1] = autoregression.adjust_lag2_corrcoef(
                    GAMMA[i, 0], GAMMA[i, 1]
                )

        # estimate the parameters of the AR(p) model from the autocorrelation
        # coefficients
        PHI = np.empty((n_cascade_levels, ar_order + 1))
        for i in range(n_cascade_levels):
            PHI[i, :] = autoregression.estimate_ar_params_yw(GAMMA[i, :])

        self._print_ar_params(PHI, False)

        # discard all except the p-1 last cascades because they are not needed for
        # the AR(p) model
        X = X[-ar_order:, :, :]

        # initialize the random generators
        if noise_method is not None:
            randgen_prec = []
            randgen_motion = []
            np.random.seed(seed)
            for j in range(n_ens_members):
                rs = np.random.RandomState(seed)
                randgen_prec.append(rs)
                seed = rs.randint(0, high=1e9)
                rs = np.random.RandomState(seed)
                randgen_motion.append(rs)
                seed = rs.randint(0, high=1e9)

        X_min = np.min(X)

        if noise_method is not None:
            # get methods for perturbations
            init_noise, generate_noise = noise.get_method(noise_method)

            # initialize the perturbation generator for the precipitation field
            pp = init_noise(X, **noise_kwargs)

            if noise_stddev_adj:
                print("Computing noise adjustment factors... ", end="")
                sys.stdout.flush()
                starttime = time.time()

                noise_std_coeffs = noise.utils.compute_noise_stddev_adjs(
                    X[-1, :, :],
                    R_thr,
                    X_min,
                    filter,
                    decomp_method,
                    10,
                    conditional=True,
                    num_workers=num_workers,
                )

                print("%.2f seconds." % (time.time() - starttime))
            else:
                noise_std_coeffs = np.ones(n_cascade_levels)

        if mask_method == "incremental":
            # initialize the structuring element
            struct = scipy.ndimage.generate_binary_structure(2, 1)
            # iterate it to expand it nxn
            n = timestep / kmperpixel
            struct = scipy.ndimage.iterate_structure(struct, int((n - 1) / 2.0))

        if vel_pert_method is not None:
            init_vel_noise, generate_vel_noise = noise.get_method(vel_pert_method)

            # initialize the perturbation generators for the motion field
            vps = []
            for j in range(n_ens_members):
                kwargs = {
                    "randstate": randgen_motion[j],
                    "p_pert_par": vp_par,
                    "p_pert_perp": vp_perp,
                }
                vp_ = init_vel_noise(V, 1.0 / kmperpixel, timestep, **kwargs)
                vps.append(vp_)

        D = [None for j in range(n_ens_members)]

        # replicate the input precipitation fields into a four-dimensional array
        # containing all ensemble members
        X = np.stack([X.copy() for i in range(n_ens_members)])

        # define global variables

        self.timestep = timestep
        self.n_ens_members = n_ens_members
        self.ar_order = ar_order
        self.R_thr = R_thr
        self.R_min = R_min
        self.dask_imported = dask_imported
        self.num_workers = num_workers
        self.callback = callback
        self.return_output = return_output

        self.wet_thr = wet_thr
        self.expl_variance = expl_variance

        self.noise_method = noise_method
        self.generate_noise = generate_noise
        self.pp = pp
        self.randgen_prec = randgen_prec
        self.noise_std_coeffs = noise_std_coeffs

        self.decomp_method = decomp_method
        self.n_cascade_levels = n_cascade_levels
        self.filter = filter
        self.MASK_thr = MASK_thr

        self.V = V
        self.D = D
        self.X = X
        self.PHI = PHI

        self.extrap_method = extrap_method
        self.extrap_kwargs = extrap_kwargs

        self.use_precip_mask = use_precip_mask
        self.mask_method = mask_method
        self.use_probmatching = use_probmatching
        self.vel_pert_method = vel_pert_method

        if vel_pert_method is not None:
            self.generate_vel_noise = generate_vel_noise
            self.vps = vps

        if use_precip_mask and mask_method == "incremental":
            self.struct = struct

    def predict(self, n_timesteps=1):

        print("Starting prediction.")

        sys.stdout.flush()
        starttime = time.time()

        # fetch global variables

        timestep = self.timestep
        n_ens_members = self.n_ens_members
        ar_order = self.ar_order
        R_thr = self.R_thr
        R_min = self.R_min
        dask_imported = self.dask_imported
        num_workers = self.num_workers

        noise_method = self.noise_method
        generate_noise = self.generate_noise
        pp = self.pp
        randgen_prec = self.randgen_prec
        noise_std_coeffs = self.noise_std_coeffs

        decomp_method = self.decomp_method
        n_cascade_levels = self.n_cascade_levels
        filter = self.filter
        MASK_thr = self.MASK_thr

        V = self.V
        D = self.D
        X = self.X
        PHI = self.PHI

        extrap_method = self.extrap_method
        extrap_kwargs = self.extrap_kwargs

        use_probmatching = self.use_probmatching
        use_precip_mask = self.use_precip_mask
        mask_method = self.mask_method

        if use_precip_mask and mask_method == "incremental":
            struct = self.struct

        vel_pert_method = self.vel_pert_method

        if vel_pert_method is not None:
            generate_vel_noise = self.generate_vel_noise
            vps = self.vps

        # iterate each time step
        for t in range(n_timesteps):

            # iterate each ensemble member
            def worker(j):

                # compute the cascade decompositions of the input precipitation fields
                X_d = []

                for i in range(ar_order):
                    X_ = decomp_method(X[j, i, :, :], filter, MASK=MASK_thr)
                    X_d.append(X_)

                # normalize the cascades and rearrange them into a four-dimensional array
                # of shape (n_cascade_levels,ar_order+1,m,n) for the autoregressive model
                X_c, mu, sigma = self._stack_cascades(X_d, n_cascade_levels)
                X_d = None

                if noise_method is not None:
                    # generate noise field
                    # EPS = generate_noise(pp, randstate=randgen_prec[j])
                    EPS = generate_noise(pp, seed=None)
                    # decompose the noise field into a cascade
                    EPS = decomp_method(EPS, filter)
                else:
                    EPS = None

                if use_precip_mask:
                    MASK_prec = X[j, i, :, :] >= R_thr
                    if mask_method == "incremental":
                        MASK_prec = scipy.ndimage.morphology.binary_dilation(
                            MASK_prec, struct
                        )

                # iterate the AR(p) model for each cascade level
                for i in range(n_cascade_levels):
                    # normalize the noise cascade
                    if EPS is not None:
                        EPS_ = (EPS["cascade_levels"][i, :, :] - EPS["means"][i]) / EPS[
                            "stds"
                        ][i]
                        EPS_ *= noise_std_coeffs[i]
                    else:
                        EPS_ = None

                    PHI_ = PHI[i, :]

                    # apply AR(p) process to cascade level
                    X_c[i, :, :, :] = autoregression.iterate_ar_model(
                        X_c[i, :, :, :], PHI_, EPS=EPS_
                    )

                EPS = None
                EPS_ = None

                # compute the recomposed precipitation field(s) from the cascades
                # obtained from the AR(p) model(s)
                X_c_ = self._recompose_cascade(X_c, mu, sigma)

                if use_precip_mask:
                    # apply the precipitation mask to prevent generation of new
                    # precipitation into areas where it was not originally
                    # observed
                    X_c_[~MASK_prec] = X_c_.min()

                if use_probmatching:
                    ## adjust the conditional CDF of the forecast (precipitation
                    ## intensity above the threshold R_thr) to match the most
                    ## recently observed precipitation field
                    X_c_ = probmatching.nonparam_match_empirical_cdf(
                        X_c_, X[j, -1, :, :]
                    )

                # compute the perturbed motion field
                if vel_pert_method is not None:
                    V_ = V + generate_vel_noise(vps[j], t * timestep)
                else:
                    V_ = V

                # advect the recomposed precipitation field to obtain the forecast
                # for time step t
                # extrap_kwargs.update({"D_prev":D[j], "return_displacement":True})
                # X_f_,D_ = extrap_method(X_c_, V_, 1, outval=R_min, **extrap_kwargs)
                # D[j] = D_
                # X_f_ = X_f_[0]

                # update stack
                for lag in range(ar_order - 1):
                    X[j, lag, :, :] = X[j, lag + 1, :, :]
                X[j, -1, :, :] = X_c_

            res = []
            for j in range(n_ens_members):
                if not dask_imported or n_ens_members == 1:
                    res.append(worker(j))
                else:
                    res.append(dask.delayed(worker)(j))

            X_f_ = (
                dask.compute(*res, num_workers=num_workers)
                if dask_imported and n_ens_members > 1
                else res
            )
            res = None

            # advect the recomposed precipitation field to obtain the forecast
            # for time step t
            # extrap_kwargs.update({"D_prev":D[j], "return_displacement":True})
            # X_f_,D_ = extrap_method(X_c_, V_, 1, outval=R_min, **extrap_kwargs)
            # D[j] = D_
            # X_f_ = X_f_[0]

            # advect all the recomposed precipitation fields to obtain the forecast
            # (i.e. transform them back into the Eulerian coordinates)
            def worker(j):

                # compute the perturbed motion field
                if vel_pert_method is not None:
                    V_ = V + generate_vel_noise(vps[j], t * timestep)
                else:
                    V_ = V

                for i in range(ar_order):
                    X[j, i, :, :] = extrap_method(
                        X[j, i, :, :], V_, n_timesteps, R_min, **extrap_kwargs
                    )[-1]

            res = []
            for j in range(n_ens_members):
                if not dask_imported or n_ens_members == 1:
                    worker(j)
                else:
                    res.append(dask.delayed(worker)(j))

            dask.compute(
                *res, num_workers=num_workers
            ) if dask_imported and n_ens_members > 1 else res
            res = None

            # update global stack
            self.X = X

        print("%.2f seconds." % (time.time() - starttime))

    def update(self, Z, B=None, alpha=0.5):

        if np.any(~np.isfinite(Z)):
            raise ValueError("Z contains non-finite values")

        print("Starting update.")

        sys.stdout.flush()
        starttime = time.time()

        # fetch global variables
        n_ens_members = int(self.n_ens_members / 2 + 1)
        wet_thr = self.wet_thr
        expl_variance = self.expl_variance
        X = self.X[:, -1, :, :]
        use_probmatching = self.use_probmatching

        # get a matrix view of X and Z
        oshape = X.shape
        # Z = Z.reshape((n_ens_members, -1))
        # X = X.reshape((n_ens_members, -1))
        Z = Z.reshape((22, -1))
        X = X.reshape((42, -1))

        # compute proportion of wet members for each grid point
        x_porportion_of_wet = np.sum(X[:n_ens_members, :] > 0, axis=0) / float(
            n_ens_members
        )
        z_porportion_of_wet = np.sum(Z[:n_ens_members, :] > 0, axis=0) / float(
            n_ens_members
        )
        idxWet = np.logical_and(
            x_porportion_of_wet >= wet_thr, z_porportion_of_wet >= wet_thr
        )

        # build full data matrix
        Y = np.concatenate((X, Z), axis=0)

        # transform all points into new space (PCA)
        Y_h, model = self._hx(Y, expl_variance)
        # X_h = Y_h[:n_ens_members,:]
        # Z_h = Y_h[n_ens_members:,:]
        X_h = model.transform(X)
        Z_h = model.transform(Z)
        n_components = X_h.shape[1]

        # only with wet pixels
        if wet_thr > 0:
            h_components = model.components_.copy()
            # Y_h_wet = ( Y[:,idxWet] - model.mean_[idxWet] ).dot( h_components[:,idxWet].T )
            # X_h_wet = Y_h_wet[:n_ens_members,:]
            # Z_h_wet = Y_h_wet[n_ens_members:,:]
            X_h_wet = (X[:n_ens_members, idxWet] - model.mean_[idxWet]).dot(
                h_components[:, idxWet].T
            )
            Z_h_wet = (Z[:n_ens_members, idxWet] - model.mean_[idxWet]).dot(
                h_components[:, idxWet].T
            )
        else:
            X_h_wet = X_h
            Z_h_wet = Z_h

        model

        # compute error covariance matrices

        ## prior
        P_h = 0
        X_h_wet_mean = X_h_wet.mean(axis=0)
        for i in range(n_ens_members):
            X_e = X_h_wet[i, :] - X_h_wet_mean
            P_h += np.outer(X_e, X_e)
        P_h /= n_ens_members - 1

        print(P_h)

        ## pseudo-observations
        R_h = 0
        Z_h_wet_mean = Z_h_wet.mean(axis=0)
        for i in range(n_ens_members):
            Z_e = Z_h_wet[i, :] - Z_h_wet_mean
            R_h += np.outer(Z_e, Z_e)
        R_h /= n_ens_members - 1
        R_h *= 1.2

        print(R_h)

        # assume P and R are diagonal
        P_h = np.diag(P_h)
        R_h = np.diag(R_h)

        # Kalman gain
        K_h = P_h / (R_h + P_h)

        print(K_h)

        #
        if B is not None:
            K_h = K_h * (1 - alpha) + B * alpha

        # print(K_h)
        # print(model.explained_variance_ratio_)

        # update
        for i in range(n_ens_members - 1):
            X_h[i, :] += K_h * (Z_h[i, :] - X_h[i, :])

        for i in range(n_ens_members - 1):
            X_h[n_ens_members + i - 1, :] += K_h * (
                Z_h[-1, :] - X_h[n_ens_members + i - 1, :]
            )

        # trasform the analysis back to original (transformed) space
        X = model.inverse_transform(X_h)

        if use_probmatching:
            ## adjust the conditional CDF of the forecast (precipitation
            ## intensity above the threshold R_thr) to match the most
            ## recently observed precipitation field

            K = np.sum(K_h * model.explained_variance_ratio_)
            K /= np.sum(model.explained_variance_ratio_)

            print("K = %.3f" % K)

        for i in range(n_ens_members - 1):
            M = self._resample(self.X[i, -1, :, :], Z[i, :], 1 - K)
            X[i, :] = probmatching.nonparam_match_empirical_cdf(X[i, :], M)

        for i in range(n_ens_members - 1):
            M = self._resample(self.X[n_ens_members + i - 1, -1, :, :], Z[-1, :], 1 - K)
            X[n_ens_members + i - 1, :] = probmatching.nonparam_match_empirical_cdf(
                X[n_ens_members + i - 1, :], M
            )

        self.X[:, -1, :, :] = X.reshape(oshape)

        print("%.2f seconds." % (time.time() - starttime))

    def _hx(self, X, explained_variance):
        """
        PCA decomposition method.
        """

        model = PCA(n_components=explained_variance, svd_solver="full")
        model = model.fit(X)  # (n_samples, n_features)
        X_ = model.transform(X)

        return X_, model

    def _resample(self, a, b, weight):
        """merge two distributions"""

        assert a.size == b.size

        asort = np.sort(a.flatten())[::-1]
        bsort = np.sort(b.flatten())[::-1]
        n = asort.shape[0]

        # resample
        idxsamples = np.random.binomial(1, weight, n).astype(bool)
        csort = bsort.copy()
        csort[idxsamples] = asort[idxsamples]
        csort = np.sort(csort)[::-1]

        return csort

    def _check_inputs(self, X, V, ar_order):
        if len(X.shape) != 3:
            raise ValueError("X must be a three-dimensional array")
        if X.shape[0] < ar_order + 1:
            raise ValueError("X.shape[0] < ar_order+1")
        if len(V.shape) != 3:
            raise ValueError("V must be a three-dimensional array")
        if X.shape[1:3] != V.shape[1:3]:
            raise ValueError(
                "dimension mismatch between X and V: shape(X)=%s, shape(V)=%s"
                % (str(X.shape), str(V.shape))
            )

    def _print_ar_params(self, PHI, include_perturb_term):
        print("****************************************")
        print("* AR(p) parameters for cascade levels: *")
        print("****************************************")

        n = PHI.shape[1]

        hline_str = "---------"
        for k in range(n):
            hline_str += "---------------"

        print(hline_str)
        title_str = "| Level |"
        for k in range(n - 1):
            title_str += "    Phi-%d     |" % (k + 1)
        title_str += "    Phi-0     |"
        print(title_str)
        print(hline_str)

        fmt_str = "| %-5d |"
        for k in range(n):
            fmt_str += " %-12.6f |"

        for k in range(PHI.shape[0]):
            print(fmt_str % ((k + 1,) + tuple(PHI[k, :])))
            print(hline_str)

    def _print_corrcoefs(self, GAMMA):
        print("************************************************")
        print("* Correlation coefficients for cascade levels: *")
        print("************************************************")

        m = GAMMA.shape[0]
        n = GAMMA.shape[1]

        hline_str = "---------"
        for k in range(n):
            hline_str += "----------------"

        print(hline_str)
        title_str = "| Level |"
        for k in range(n):
            title_str += "     Lag-%d     |" % (k + 1)
        print(title_str)
        print(hline_str)

        fmt_str = "| %-5d |"
        for k in range(n):
            fmt_str += " %-13.6f |"

        for k in range(m):
            print(fmt_str % ((k + 1,) + tuple(GAMMA[k, :])))
            print(hline_str)

    def _stack_cascades(self, X_d, n_levels):
        X_c = []
        mu = np.empty(n_levels)
        sigma = np.empty(n_levels)

        n_inputs = len(X_d)

        for i in range(n_levels):
            X_ = []
            for j in range(n_inputs):
                mu_ = X_d[j]["means"][i]
                sigma_ = X_d[j]["stds"][i]
                if j == n_inputs - 1:
                    mu[i] = mu_
                    sigma[i] = sigma_
                X__ = (X_d[j]["cascade_levels"][i, :, :] - mu_) / sigma_
                X_.append(X__)
            X_c.append(np.stack(X_))

        return np.stack(X_c), mu, sigma

    def _recompose_cascade(self, X, mu, sigma):
        X_rc = [(X[i, -1, :, :] * sigma[i]) + mu[i] for i in range(len(mu))]
        X_rc = np.sum(np.stack(X_rc), axis=0)

        return X_rc

    def _semilagr_fortran(self, R, UV, net, outval=np.nan, **kwargs):
        # resize motion fields by factor f (for advection)
        U = UV[0, :, :]
        V = UV[1, :, :]
        f = 0.3
        if f < 1:
            Ures = cv2.resize(U, (0, 0), fx=f, fy=f)
            Vres = cv2.resize(V, (0, 0), fx=f, fy=f)
        else:
            Ures = U
            Vres = V

        # Call MAPLE routine for advection
        R_e = semilagr.ree_epol_slio(R, Vres, Ures, net)
        R_e[np.isnan(R_e)] = outval
        R_e = np.rollaxis(R_e, 2, 0)

        return R_e

    @property
    def getforecast(self):
        return np.array(self.X[:, -1, :, :].copy().squeeze())
