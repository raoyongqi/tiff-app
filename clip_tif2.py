# import rasterio
# from rasterio.mask import mask
# import geopandas as gpd

# def clip_tif_with_geojson(tif_path, geojson_path, output_path):
#     # 读取GeoJSON文件
#     geojson = gpd.read_file(geojson_path)

#     # 打开TIF文件
#     with rasterio.open(tif_path) as src:
#         # 根据GeoJSON的几何形状剪切TIF
#         out_image, out_transform = mask(src, geojson.geometry, crop=True)
        
#         # 更新元数据
#         out_meta = src.meta.copy()
#         out_meta.update({"driver": "GTiff",
#                          "height": out_image.shape[1],
#                          "width": out_image.shape[2],
#                          "transform": out_transform})

#     # 保存剪切后的TIF文件
#     with rasterio.open(output_path, "w", **out_meta) as dest:
#         dest.write(out_image)

# # 使用示例
# tif_path = 'tiff_folder/wc2.1_10m_bio_1.tif'
# geojson_path = 'geojson/Pan-Tibetan Highlands (Liu et al._2022).geojson'
# output_path = 'cliped_folder/file_cropped.tif'

# clip_tif_with_geojson(tif_path, geojson_path, output_path)
import rasterio
from rasterio.mask import mask
from shapely.geometry import shape
import geopandas as gpd
import json
import numpy as np

# 输入 TIFF 文件路径和 GeoJSON 文件路径
tiff_path = 'tiff_folder/wc2.1_10m_bio_1.tif'
geojson_path = 'geojson/Pan-Tibetan Highlands (Liu et al._2022).geojson'
output_path = 'cliped_folder/file_cropped.tif'

# 读取 GeoJSON
with open(geojson_path) as f:
    geojson = json.load(f)

# 读取 TIFF 文件
with rasterio.open(tiff_path) as src:
    # 将 GeoJSON 转换为 shapely 几何对象
    geometries = [shape(feature["geometry"]) for feature in geojson["features"]]

    # 使用 GeoJSON 进行剪切，并处理缺失值
    out_image, out_transform = mask(src, geometries, crop=True, nodata=np.nan)

    # 更新元数据
    out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform,
        "nodata": np.nan
    })

    # 保存结果
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(out_image)

print(f"Clipped image saved to {output_path}")
