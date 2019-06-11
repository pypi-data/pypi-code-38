import numpy as np

from . import utils
from .losses import ActivationMaximization


def keras_visualize_cam(dynamic_import, model, filter_indices, seed_img, text=None):
    import cv2
    from .optimizer import Optimizer

    filter_indices = utils.listify(filter_indices)

    Dense = dynamic_import.bring('layers.Dense')
    Convolution2D = dynamic_import.bring('layers.Convolution2D')
    _Pooling2D = dynamic_import.bring('layers.pooling._Pooling2D')

    K = dynamic_import.bring('backend')

    layer_idx = None
    for idx, layer in utils.reverse_enumerate(model.layers):
        if isinstance(layer, Dense):
            layer_idx = idx
            break

    penultimate_layer_idx = None
    for idx, layer in utils.reverse_enumerate(model.layers[:layer_idx - 1]):
        if isinstance(layer, (Convolution2D, _Pooling2D)):
            penultimate_layer_idx = idx
            break

    if penultimate_layer_idx is None:
        raise ValueError('Unable to determine penultimate `Convolution2D` or `Pooling2D` '
                         'layer for layer_idx: {}'.format(layer_idx))
    assert penultimate_layer_idx < layer_idx

    losses = [
        (ActivationMaximization(model.layers[layer_idx], filter_indices), 1)
    ]

    penultimate_output = model.layers[penultimate_layer_idx].output
    opt = Optimizer(model.input, losses, K, wrt=penultimate_output)

    _, grads, penultimate_output_value = opt.minimize(seed_img, max_iter=1, jitter=0, verbose=False)

    # We are minimizing loss as opposed to maximizing output as with the paper.
    # So, negative gradients here mean that they reduce loss, maximizing class probability.
    grads *= -1

    # Average pooling across all feature maps.
    # This captures the importance of feature map (channel) idx to the output
    s_idx, c_idx, row_idx, col_idx = utils.get_img_indices(K.image_dim_ordering())
    weights = np.mean(grads, axis=(s_idx, row_idx, col_idx))

    # Generate heatmap by computing weight * output over feature maps
    s, ch, rows, cols = utils.get_img_shape(penultimate_output, K)
    heatmap = np.ones(shape=(rows, cols), dtype=np.float32)
    for i, w in enumerate(weights):
        heatmap += w * penultimate_output_value[utils.slicer(K.image_dim_ordering())[0, i, :, :]]

    # The penultimate feature map size is definitely smaller than input image.
    s, ch, rows, cols = utils.get_img_shape(model.input, K)
    heatmap = cv2.resize(heatmap, (cols, rows), interpolation=cv2.INTER_CUBIC)

    # ReLU thresholding, normalize between (0, 1)
    heatmap = np.maximum(heatmap, 0)
    heatmap /= np.max(heatmap)

    # Convert to heatmap and zero out low probabilities for a cleaner output.
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    heatmap_colored[np.where(heatmap <= 0.2)] = 0

    seed_img_rgb = seed_img.astype(np.uint8)

    def remove_alpha_channel(img):
        a_channel, b_channel, g_channel, r_channel = cv2.split(img)

        return cv2.merge((b_channel, g_channel, r_channel))

    def greyscale_to_rgb(img):
        return cv2.merge((img, img, img))

    if seed_img_rgb.shape[2] == 4:
        seed_img_rgb = remove_alpha_channel(seed_img_rgb)
    elif seed_img_rgb.shape[2] == 1:
        seed_img_rgb = greyscale_to_rgb(seed_img_rgb)

    overlay_image = cv2.addWeighted(seed_img_rgb, 1, heatmap_colored, 1, 0)

    if text:
        cv2.putText(overlay_image, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)

    def convert_to_jpg(img):
        return cv2.imencode('.jpg', img)[1]

    return convert_to_jpg(seed_img_rgb), convert_to_jpg(heatmap_colored), convert_to_jpg(overlay_image)
