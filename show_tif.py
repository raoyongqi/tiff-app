import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np
# 打开 TIFF 文件
tif_file = "cliped_folder/output_clipped.tif"
with rasterio.open(tif_file) as src:
    # 显示栅格数据
    show(src)
    crs = src.crs
    print(crs)
    plt.show()
    data = src.read(1) 
# 将数据转换为一维数组，并移除无效值（如 NaN 或无效值）
data = data.flatten()
data = data[~np.isnan(data)]
data = data[data != src.nodata]

# 生成箱线图
plt.figure(figsize=(10, 6))
plt.boxplot(data, vert=False)
plt.title('Boxplot of TIFF Data')
plt.xlabel('Values')
plt.show()