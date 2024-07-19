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
            # 读取所有波段并转换为浮点型
            image_data = src.read().astype(np.float32)

            # 创建一个临时的内存文件来保存转换后的图像
            with rasterio.MemoryFile() as memfile:
                with memfile.open(
                    driver="GTiff",
                    height=image_data.shape[1],
                    width=image_data.shape[2],
                    count=image_data.shape[0],
                    dtype="float32",
                    crs=src.crs,
                    transform=src.transform,
                    nodata=np.nan,
                ) as dataset:
                    dataset.write(image_data)

                    # 使用 GeoJSON 进行剪切，并处理缺失值
                    out_image, out_transform = mask(dataset, geometries, crop=True, nodata=np.nan)

                    # 更新元数据
                    out_meta = dataset.meta.copy()
                    out_meta.update({
                        "driver": "GTiff",
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform,
                        "dtype": "float32",  # 保持数据类型为浮点型
                        "nodata": np.nan
                    })

                    # 保存剪切后的结果
                    with rasterio.open(output_path, "w", **out_meta) as dest:
                        dest.write(out_image)

        print(f"Clipped image saved to {output_path}")
