"""
Module with methods for handling JPEG2000 images
"""

# TODO verify these orders somewhere, and 8a band vs 8 band
SENTINAL2_IMG_TYPES = {
    # 10m+
    'true_color': ('04', '03', '02'),
    'false_color_infrared': ('08', '04', '03'),
    # 20m+
    'false_color_urban': ('12', '11', '04'),
    'agriculture': ('11', '8A', '02'), #added A
    'atmospheric_penetration': ('12', '11', '8A'),
    'healthy_vegetation': ('8A', '11', '02'), #added A
    'land_Water': ('8A', '11', '04'), #added A
    'true_color_atmospheric_removal': ('12', '8A', '03'), #added A
    'shortwave_infrared': ('12', '8A', '04'), #added A
    'vegetation_analysis': ('11', '8A', '04') #added A
    }


def product_img_bands(path_data, product_id, res="10m", img_type='true_color'):
    """
    Read data for RGB bands from Sentinel SAFE formatted products

    Parameters
    ==========
    path_data: str
        Path to directory containing Sentinel SAFE formatted products
    product_id: str
        Basename of Sentinel product, omitting the `.SAFE` extension
    res: str
        Resolution of bands to extract (one of `10m`, `20m`, `60m`)
    img_type: str
        Name of the image type to extract bands for. This name corresponds to
        the bands that when composed produce that type of image.

    Returns
    =======
    bands: list of ndarray
        The data for the bands corresponding to those defined by the image type
        requested.
    profile: dict
        Image profile metadata from rasterio object
    """
    import os
    import rasterio

    from geotoys.system import list_ext

    resolutions = ["10m", "20m", "60m"]

    if res not in resolutions:
        raise ValueError(f"`res` must be one of {' '.join(resolutions)}")

    if img_type not in IMG_TYPES.keys():
        raise ValueError(f"`img_type` must be one of {' '.join(IMG_TYPES.keys())}")

    _logger.info(f"Creating {img_type} JPEG of {product_id}...")

    # Create band search strings for finding bands by label
    # Add resolution if Level-2A product
    band_labels = [ f"B{b}" for b in SENTINEL2_IMG_TYPES[img_type]]
    if 'L2B' in product_id:
        band_labels = [f"{b}_{res}" for b in band_labels]

    jp2s = list_ext(os.path.join(path_data, f"{product_id}.SAFE"), '.jp2')

    # Loop through jp2 files and collect data for desired bands/resolution
    bands = list()
    first_iter = True
    for b in band_labels:
        for jp2 in jp2s:
            if b in jp2:
                _logger.info(f"Reading data for: {os.path.basename(jp2)}")
                with rasterio.open(jp2) as src:
                    bands.append(src.read(1))
                    if first_iter:
                        profile = src.profile
                        first_iter = False
                    src.close()

    return bands, profile


def jp2_to_jpeg(path_data, path_output, product_id, res="10m", img_type='true_color'):
    """
    Convert a Sentinel product's JPEG2000 to JPEG RGB
    """
    import os
    import uuid

    bands, src_profile = product_img_bands(path_data, product_id, res=res, img_type=img_type)

    fp_dst = os.path.join(path_output, f"{product_id}_{img_type}.jpg")
    os.makedirs(os.path.dirname(fp_dst), exist_ok=True)

    _save_jpeg_rgb(bands, src_profile, fp_dst, band_count=len(IMG_TYPES[img_type]))

    # Create summary as done in annotation data
    summary = {
        "id": uuid.uuid4(),
        "file_name": os.path.basename(fp_dst),
        "width": src_profile["width"],
        "height": src_profile["height"],
        "crs": src_profile["crs"].to_epsg()
        }

    return summary
