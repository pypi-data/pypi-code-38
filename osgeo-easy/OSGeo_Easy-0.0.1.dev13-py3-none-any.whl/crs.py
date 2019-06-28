import osgeo.osr as osr

DEFAULT_EPSG = 4326


def get_spatial_reference(crs_ref) -> osr.SpatialReference:
    """
    Always return a osr.SpatialReference
    :param crs_ref:
    :return:
    """
    if isinstance(crs_ref, int):
        proj_from = osr.SpatialReference()
        proj_from.ImportFromEPSG(crs_ref)
    elif isinstance(crs_ref, osr.SpatialReference):
        proj_from = crs_ref
    else:
        raise TypeError
    return proj_from


def get_coordinate_transform(crs_from, crs_to) -> osr.CoordinateTransformation:
    """

    :param crs_from: EPSG code or osr.SpatialReference object
    :param crs_to: EPSG code or osr.SpatialReference object
    :return:
    """
    proj_from = get_spatial_reference(crs_from)
    proj_to = get_spatial_reference(crs_to)
    return osr.CoordinateTransformation(proj_from, proj_to)
