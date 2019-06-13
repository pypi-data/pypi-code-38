import numpy as np


def load_image(path, input_shape, channels_first, dtype):
    import cv2

    try:
        from urllib import urlopen
    except ImportError:
        from urllib.request import urlopen

    def img_to_array():
        x = np.asarray(img, dtype=dtype)
        if len(x.shape) == 3:
            if channels_first:
                x = x.transpose(2, 0, 1)
        elif len(x.shape) == 2:
            if channels_first:
                x = x.reshape((1, x.shape[0], x.shape[1]))
            else:
                x = x.reshape((x.shape[0], x.shape[1], 1))
        else:
            raise ValueError('Unsupported image shape: ', x.shape)

        return x

    def add_alpha_channel(img):
        b_channel, g_channel, r_channel = cv2.split(img)

        alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255

        return cv2.merge((alpha_channel, b_channel, g_channel, r_channel))

    def load_img_using_opencv():
        file_bytes = np.asarray(bytearray(image_data), dtype=np.uint8)
        loaded_img = cv2.imdecode(file_bytes, 1)
        loaded_img = cv2.resize(loaded_img, (rows, cols))

        image_channels = loaded_img.shape[2]

        if channels == 4 and image_channels == 3:
            return add_alpha_channel(loaded_img)

        return loaded_img

    rows, cols, channels = input_shape

    image_data = urlopen(path).read()
    img = load_img_using_opencv()

    return img_to_array()
