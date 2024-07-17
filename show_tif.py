import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt

# 打开 TIFF 文件
tif_file = "tiff_folder/wc2.1_10m_bio_1.tif"
with rasterio.open(tif_file) as src:
    # 显示栅格数据
    show(src)
    crs = src.crs
    print(crs)
    plt.show()
