
# feature_names.extend(['lon', 'lat'])

# # 输出文件夹

# os.makedirs(output_folder, exist_ok=True)

# # 加载每个模型并进行预测
# for model_file in model_files:
#     model = joblib.load(model_file)
    
#     # 进行预测
#     y_pred = model.predict(data_with_coords)
    
#     # 将预测结果转换为二维数组
#     y_pred_2d = y_pred.reshape((rows, cols))
    
#     # 保存预测结果为tif文件
#     model_name = os.path.splitext(os.path.basename(model_file))[0]
#     output_file = os.path.join(output_folder, f'predicted_{model_name}.tif')
#     save_tif(output_file, y_pred_2d, profiles[0])

#     print(f"预测结果已保存到 {output_file}")
import os
import joblib
import rasterio
import numpy as np
import pandas as pd

# 读取tif文件并提取数据和元数据，包括经纬度信息
def read_tif_with_coords(file_path):
    with rasterio.open(file_path) as src:
        data = src.read(1)  # 读取第一波段的数据
        profile = src.profile
        transform = src.transform  # 获取仿射变换信息
        width = src.width
        height = src.height

        # 生成所有像素的行列号
        rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')

        # 将行列号转换为地理坐标（经纬度）
        xs, ys = rasterio.transform.xy(transform, rows, cols)

    return data, profile, np.array(xs), np.array(ys)

# 保存预测结果为tif文件
def save_tif(file_path, data, profile):
    with rasterio.open(file_path, 'w', **profile) as dst:
        dst.write(data, 1)

# 获取特征名称
def get_feature_name(file_name):
    base_name = os.path.basename(file_name)
    feature_name = base_name.replace('cropped_', '').replace('.tif', '')
    return feature_name


tif_folder = 'cliped_folder'  # 替换为实际tif文件夹路径
model_folder = 'models'  # 替换为实际模型文件夹路径


tif_files = [os.path.join(tif_folder, f) for f in os.listdir(tif_folder) if f.endswith('.tif')]
model_files = [os.path.join(model_folder, f) for f in os.listdir(model_folder) if f.endswith('.joblib')]

# 获取特征名称
feature_names = [get_feature_name(f) for f in tif_files]

# 加载所有tif文件的数据和经纬度信息
data_list = []
profiles = []
lons, lats = None, None

for i, file in enumerate(tif_files):
    data, profile, xs, ys = read_tif_with_coords(file)
    data_list.append(data)
    profiles.append(profile)
    if i == 0:  # 只保存第一个tif的经纬度信息
        lons, lats = xs, ys

# 将数据和经纬度转换为二维数组
data_stack = np.stack(data_list, axis=-1)
rows, cols, bands = data_stack.shape
data_2d = data_stack.reshape((rows * cols, bands))

# 添加经纬度信息作为特征
coords_2d = np.stack((lons.flatten(), lats.flatten()), axis=1)
data_with_coords = np.hstack((data_2d, coords_2d))

# 为经纬度添加特征名称
feature_names.extend(['lon', 'lat'])

# 将数据转换为DataFrame
df = pd.DataFrame(data_with_coords, columns=feature_names)

output_folder = 'rf_result'  # 替换为实际输出文件夹路径
os.makedirs(output_folder, exist_ok=True)

# 加载每个模型并进行预测
for model_file in model_files:
    model = joblib.load(model_file)
    
    # 进行预测
    y_pred = model.predict(df)
    
    # 将预测结果转换为二维数组
    y_pred_2d = y_pred.reshape((rows, cols))
    
    # 保存预测结果为tif文件
    model_name = os.path.splitext(os.path.basename(model_file))[0]
    output_file = os.path.join(output_folder, f'predicted_{model_name}.tif')
    save_tif(output_file, y_pred_2d, profiles[0])

    print(f"预测结果已保存到 {output_file}")
