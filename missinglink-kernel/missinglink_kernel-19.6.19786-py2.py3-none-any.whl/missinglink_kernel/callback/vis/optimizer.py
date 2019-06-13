import pprint
from collections import OrderedDict

import numpy as np

from . import utils


class Optimizer(object):
    def __init__(self, img_input, losses, K, wrt=None):
        """Creates an optimizer that minimizes weighted loss function.

        Args:
            img_input: 4D image input tensor to the model of shape: `(samples, channels, rows, cols)`
                if dim_ordering='th' or `(samples, rows, cols, channels)` if dim_ordering='tf'.
            losses: List of ([Loss](vis.losses#Loss), weight) tuples.
            wrt: Short for, with respect to. This instructs the optimizer that the aggregate loss from `losses`
                should be minimized with respect to `wrt`. `wrt` can be any tensor that is part of the model graph.
                Default value is set to None which means that loss will simply be minimized with respect to `img_input`.
        """
        self.img = img_input
        self.loss_functions = []
        self.wrt = self.img if wrt is None else wrt

        overall_loss = K.variable(0.)

        for loss, weight in losses:
            # Perf optimization. Don't build loss function with 0 weight.
            if weight != 0:
                loss_fn = weight * loss.build_loss(K)
                overall_loss += loss_fn
                # Learning phase is added so that 'test' phase can be used to disable dropout.
                self.loss_functions.append((loss.name, K.function([self.img, K.learning_phase()], [loss_fn])))

        # Compute gradient of overall with respect to `wrt` tensor.
        grads = K.gradients(overall_loss, self.wrt)[0]
        # Normalization avoids very small or large gradients and ensures a smooth gradient gradient descent process.
        grads = grads / (K.sqrt(K.mean(K.square(grads))) + K.epsilon())

        self.overall_loss_grad_wrt_fn = K.function([self.img, K.learning_phase()], [overall_loss, grads, self.wrt])

    def eval_losses(self, img):
        """Evaluates losses with respect to numpy input image.

        Args:
            img: 4D numpy array with shape: `(samples, channels, rows, cols)` if dim_ordering='th' or
                `(samples, rows, cols, channels)` if dim_ordering='tf'.

        Returns:
            A dictionary of ([Loss](vis.losses#Loss).name, loss_value) values for various losses.
        """
        losses = OrderedDict()
        for name, fn in self.loss_functions:
            # 0 learning phase for 'test'
            losses[name] = fn([img, 0])
        return losses

    @classmethod
    def rmsprop(cls, grads, cache=None, decay_rate=0.95):
        """Uses RMSProp to compute step from gradients.

        Args:
            grads: numpy array of gradients.
            cache: numpy array of same shape as `grads` as RMSProp cache
            decay_rate: How fast to decay cache

        Returns:
            A tuple of
                step: numpy array of the same shape as `grads` giving the step.
                    Note that this does not yet take the learning rate into account.
                cache: Updated RMSProp cache.
        """
        if cache is None:
            cache = np.zeros_like(grads)
        cache = decay_rate * cache + (1 - decay_rate) * grads ** 2
        # noinspection PyUnresolvedReferences
        step = -grads / np.sqrt(cache + K.epsilon())
        return step, cache

    @classmethod
    def jitter(cls, img, jitter=32, dim_ordering='default'):
        """Jitters the numpy input image randomly in width and height dimensions.
        This kind of regularization is known to produce crisper images via guided backprop.

        Args:
          img: 4D numpy array with shape: `(samples, channels, rows, cols)` if dim_ordering='th' or
                `(samples, rows, cols, channels)` if dim_ordering='tf'
          jitter: Number of pixels to jitter in width and height directions.

        Returns:
            The jittered numpy image array.
        """
        s, ch, row, col = utils.get_img_indices(dim_ordering)
        # noinspection PyUnresolvedReferences
        ox, oy = np.random.randint(-jitter, jitter + 1, 2)
        return np.roll(np.roll(img, ox, row), oy, col)

    @classmethod
    def get_seed_img(cls, seed_img, dim_ordering):
        if dim_ordering == 'th':
            seed_img = seed_img.transpose(2, 0, 1)

        # Convert to image tensor containing samples.
        seed_img = np.array([seed_img], dtype=np.float32)
        return seed_img

    def minimize(self, seed_img=None, max_iter=200,
                 jitter=8, verbose=True, dim_ordering='default'):
        """Performs gradient descent on the input image with respect to defined losses.

        Args:
            seed_img: 3D numpy array with shape: `(channels, rows, cols)` if dim_ordering='th' or
                `(rows, cols, channels)` if dim_ordering='tf'.
                Seeded with random noise if set to None. (Default value = None)
            max_iter: The maximum number of gradient descent iterations. (Default value = 200)
            jitter: The number of pixels to jitter between subsequent gradient descent iterations.
                Jitter is known to generate crisper images. (Default value = 8)
            verbose: Logs individual losses at the end of every gradient descent iteration.
                Very useful to estimate loss weight factor. (Default value = True)

        Returns:
            The tuple of `(optimized_image, grads with respect to wrt, wrt_value)` after gradient descent iterations.
        """
        seed_img = self.get_seed_img(seed_img, dim_ordering)

        cache = None
        best_loss = float('inf')
        best_img = None

        grads = None
        wrt_value = None

        for i in range(max_iter):
            if jitter > 0:
                seed_img = self.jitter(seed_img, jitter)

            # 0 learning phase for 'test'
            loss, grads, wrt_value = self.overall_loss_grad_wrt_fn([seed_img, 0])

            if verbose:
                losses = self.eval_losses(seed_img)
                print('Iteration: {}, losses: {}, overall loss: {}'.format(i + 1, pprint.pformat(losses), loss))

            # Gradient descent update.
            # It only makes sense to do this if wrt is image. Otherwise shapes wont match for the update.
            if self.wrt is self.img:
                step, cache = self.rmsprop(grads, cache)
                seed_img += step

            if loss < best_loss:
                best_loss = loss
                best_img = seed_img.copy()

        return utils.deprocess_image(best_img[0]), grads, wrt_value
