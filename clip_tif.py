# from osgeo import gdal, gdalnumeric, ogr, osr
# import os

# def clip_raster_with_shapefile(raster_path, shapefile_path, output_path):
#     # 打开栅格数据
#     raster_dataset = gdal.Open(raster_path)
#     if raster_dataset is None:
#         print(f"Failed to open raster file: {raster_path}")
#         return

#     # 获取栅格数据的投影和地理参考信息
#     projection = raster_dataset.GetProjectionRef()
#     geotransform = raster_dataset.GetGeoTransform()

#     # 打开矢量数据
#     shapefile_dataset = ogr.Open(shapefile_path)
#     if shapefile_dataset is None:
#         print(f"Failed to open shapefile: {shapefile_path}")
#         return

#     # 获取矢量图层
#     layer = shapefile_dataset.GetLayer()

#     # 创建输出栅格数据
#     driver = gdal.GetDriverByName('GTiff')
#     output_dataset = driver.Create(output_path,
#                                    raster_dataset.RasterXSize,
#                                    raster_dataset.RasterYSize,
#                                    raster_dataset.RasterCount,
#                                    raster_dataset.GetRasterBand(1).DataType)
#     output_dataset.SetProjection(projection)
#     output_dataset.SetGeoTransform(geotransform)

#     # 矢量数据的空间参考
#     source_srs = layer.GetSpatialRef()
#     target_srs = osr.SpatialReference()
#     target_srs.ImportFromWkt(projection)
#     coord_trans = osr.CoordinateTransformation(source_srs, target_srs)

#     # 使用矢量数据的几何图形进行剪切
#     gdal.Warp(output_dataset, raster_dataset,
#               cutlineDSName=shapefile_path,
#               cutlineLayer=layer.GetName(),
#               dstNodata=0,
#               outputBounds=[layer.GetExtent()[0], layer.GetExtent()[2],
#                             layer.GetExtent()[1], layer.GetExtent()[3]],
#               format='GTiff')

#     # 关闭数据集
#     output_dataset = None
#     raster_dataset = None
#     shapefile_dataset = None

#     print(f"Raster clipped and saved to: {output_path}")

# # 示例使用
# raster_file = 'tiff_folder/wc2.1_10m_bio_1.tif'
# shapefile = 'path/to/your/shapefile.shp'
# output_file = 'path/to/your/output_clipped.tif'

# clip_raster_with_shapefile(raster_file, shapefile, output_file)
from osgeo import gdal, ogr, osr
import os

def clip_raster_with_geojson(raster_path, geojson_path, output_path):
    # 打开栅格数据
    raster_dataset = gdal.Open(raster_path)
    if raster_dataset is None:
        print(f"Failed to open raster file: {raster_path}")
        return

    # 获取栅格数据的投影和地理参考信息
    projection = raster_dataset.GetProjectionRef()
    geotransform = raster_dataset.GetGeoTransform()

    # 打开 GeoJSON 文件
    geojson_dataset = ogr.Open(geojson_path)
    if geojson_dataset is None:
        print(f"Failed to open GeoJSON file: {geojson_path}")
        return

    # 获取 GeoJSON 图层
    layer = geojson_dataset.GetLayer()

    # 创建输出栅格数据
    driver = gdal.GetDriverByName('GTiff')
    output_dataset = driver.Create(output_path,
                                   raster_dataset.RasterXSize,
                                   raster_dataset.RasterYSize,
                                   raster_dataset.RasterCount,
                                   raster_dataset.GetRasterBand(1).DataType)
    output_dataset.SetProjection(projection)
    output_dataset.SetGeoTransform(geotransform)

    # 矢量数据的空间参考
    source_srs = layer.GetSpatialRef()
    target_srs = osr.SpatialReference()
    target_srs.ImportFromWkt(projection)
    coord_trans = osr.CoordinateTransformation(source_srs, target_srs)

    # 使用 GeoJSON 的几何图形进行剪切
    gdal.Warp(output_dataset, raster_dataset,
              cutlineDSName=geojson_path,
              cutlineLayer=layer.GetName(),
              dstNodata=0,
              format='GTiff')

    # 关闭数据集
    output_dataset = None
    raster_dataset = None
    geojson_dataset = None

    print(f"Raster clipped and saved to: {output_path}")

# 示例使用
raster_file = 'tiff_folder/wc2.1_10m_bio_1.tif'
geojson_file = 'path/to/your/geojson_file.geojson'
output_file = 'path/to/your/output_clipped.tif'

clip_raster_with_geojson(raster_file, geojson_file, output_file)
