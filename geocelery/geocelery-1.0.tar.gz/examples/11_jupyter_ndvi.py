from geocelery import MapReduce
import dboxmr


def ndvi_map(args):
    import numpy as np
    import dboxio

    x, y, kwargs = args

    band3_path = kwargs["band3"]
    band4_path = kwargs["band4"]
    ndvi_ds_path = kwargs["dstfile"]
    dst_nodata = kwargs["nodata"]

    nir_dsh = dboxio.DBoxDataset(band3_path)
    nir_ds = nir_dsh.GetGridAsGDALDataset(x, y)
    if not nir_ds:
        return None

    cols, rows = nir_dsh.GetGridSize(x, y)

    nir_band = nir_ds.GetRasterBand(1)
    nir_nodata = nir_band.GetNoDataValue()

    np_nir = nir_band.ReadAsArray(0, 0, cols, rows)
    nir_mask = np.equal(np_nir, nir_nodata)

    red_dsh = dboxio.DBoxDataset(band4_path)
    red_ds = red_dsh.GetGridAsGDALDataset(x, y)
    if not red_ds:
        return None

    red_band = red_ds.GetRasterBand(1)
    red_nodata = red_band.GetNoDataValue()

    np_red = red_band.ReadAsArray(0, 0, cols, rows)
    red_mask = np.equal(np_red, red_nodata)

    nodata_mask = np.logical_or(nir_mask, red_mask)

    np_nir_as32 = np_nir.astype(np.float32)
    np_red_as32 = np_red.astype(np.float32)

    result = (np_nir_as32 - np_red_as32) / (np_nir_as32 + np_red_as32)

    result = np.where(nodata_mask, dst_nodata, result)
    result = result.astype(np.float32)

    #     gdal.SetConfigOption( "DBoxDisableCache", "1" )
    ndvi_ds = dboxio.DBoxDataset(ndvi_ds_path, dboxio.GA_Update)
    ndvi_dsh = ndvi_ds.GetGridAsGDALDataset(x, y)
    if not ndvi_dsh:
        return None

    ndvi_band = ndvi_dsh.GetRasterBand(1)
    ndvi_band.WriteArray(result, 0, 0)
    ndvi_dsh.FlushCache()
    ndvi_ds.Close()
    del ndvi_ds

    ndvi_ds = dboxio.DBoxDataset(ndvi_ds_path, dboxio.GA_ReadOnly)
    ndvi_dsh = ndvi_ds.GetGridAsGDALDataset(x, y)
    if not ndvi_dsh:
        return None
    ndvi_band = ndvi_dsh.GetRasterBand(1)
    print(ndvi_band.GetStatistics(0, 1))

    return ndvi_ds.GetGridFile(x, y)


def ndvi_reduce(all_tiffs):
    return [tiff for tiff in all_tiffs if tiff is not None]


def calc_lst_ndvi(band3, band4, **kwargs):
    '''
    利用 Landsat 影像计算 ndvi，需要 urllib3
    '''
    if not band3 or not band4:
        return None, None

    import gdalconst
    from dboxapi import DBoxCCData, DBoxQuery

    band3 = DBoxCCData(band3).fullname()
    band4 = DBoxCCData(band4).fullname()

    cquery = DBoxQuery()
    all_tiles = []

    dst_nodata = -10
    jdata, status = cquery.ds_tmp(band3, gdalconst.GDT_Float32, 1, dst_nodata)
    # 调用远程服务创建一个零时文件对象
    #     print(jdata)
    if status != 200:
        print("-----------------")
        return None, None

    xoff = jdata["xtiles"]
    yoff = jdata["ytiles"]

    ndvi_ds_path = DBoxCCData(jdata["objectid"]).fullname()

    for idx in range(len(xoff)):
        for idy in range(len(yoff)):
            all_tiles.append([idx, idy, {
                "band3": band3,
                "band4": band4,
                "dstfile": ndvi_ds_path,
                "nodata": dst_nodata
            }])

    taskid = MapReduce.start(all_tiles, ndvi_map, ndvi_reduce)
    rst = MapReduce.result(taskid)

    return jdata["objectid"], [DBoxCCData(tiff).objectid() for tiff in rst]


if __name__ == "__main__":
    band3 = "c0/p3/GS_LT51300341992300BJC00_B30.DBOX"
    band4 = "c0/p4/GS_LT51300341992300BJC00_B40.DBOX"

    rst = calc_lst_ndvi(band3, band4)

    print(rst)
