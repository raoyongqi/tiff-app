from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许的HTTP头
)

@app.get("/tiff")
def get_tiff():
    tiff_path = "cliped_folder/file_cropped.tif"  # 替换为你的TIFF文件的具体路径
    if os.path.exists(tiff_path):
        return FileResponse(tiff_path, media_type='image/tiff', filename="wc2.1_10m_bio_1.tif")
    else:
        raise HTTPException(status_code=404, detail="TIFF file not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
