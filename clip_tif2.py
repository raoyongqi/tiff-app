
# import rasterio
# from rasterio.mask import mask
# from shapely.geometry import shape
# import geopandas as gpd
# import json
# import numpy as np

# # 输入 TIFF 文件路径和 GeoJSON 文件路径
# tiff_path = 'tiff_folder/wc2.1_10m_bio_1.tif'
# geojson_path = 'geojson/Pan-Tibetan Highlands (Liu et al._2022).geojson'
# output_path = 'cliped_folder/file_cropped.tif'

# # 读取 GeoJSON
# with open(geojson_path) as f:
#     geojson = json.load(f)

# # 读取 TIFF 文件
# with rasterio.open(tiff_path) as src:
#     # 将 GeoJSON 转换为 shapely 几何对象
#     geometries = [shape(feature["geometry"]) for feature in geojson["features"]]

#     # 使用 GeoJSON 进行剪切，并处理缺失值
#     out_image, out_transform = mask(src, geometries, crop=True, nodata=np.nan)

#     # 更新元数据
#     out_meta = src.meta.copy()
#     out_meta.update({
#         "driver": "GTiff",
#         "height": out_image.shape[1],
#         "width": out_image.shape[2],
#         "transform": out_transform,
#         "nodata": np.nan
#     })

#     # 保存结果
#     with rasterio.open(output_path, "w", **out_meta) as dest:
#         dest.write(out_image)

# print(f"Clipped image saved to {output_path}")
import os
import rasterio
from rasterio.mask import mask
from shapely.geometry import shape
import json
import numpy as np

# 输入文件夹路径和 GeoJSON 文件路径
tiff_folder = 'tiff_folder/'
geojson_path = 'geojson/Pan-Tibetan Highlands (Liu et al._2022).geojson'
output_folder = 'cliped_folder/'

# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 读取 GeoJSON
with open(geojson_path) as f:
    geojson = json.load(f)

# 将 GeoJSON 转换为 shapely 几何对象
geometries = [shape(feature["geometry"]) for feature in geojson["features"]]

# 遍历 TIFF 文件夹中的所有文件
for tiff_file in os.listdir(tiff_folder):
    if tiff_file.endswith('.tif'):
        tiff_path = os.path.join(tiff_folder, tiff_file)
        output_path = os.path.join(output_folder, f'cropped_{tiff_file}')

        # 读取 TIFF 文件
        with rasterio.open(tiff_path) as src:
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
