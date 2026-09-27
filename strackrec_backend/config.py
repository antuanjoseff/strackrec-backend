import os
from pathlib import Path

for var in ["PROJ_LIB", "PROJ_DATA", "GDAL_DATA"]:
    os.environ.pop(var, None)

import rasterio

RASTERIO_PROJ = Path(rasterio.__file__).resolve().parent / "proj_data"
os.environ["PROJ_DATA"] = str(RASTERIO_PROJ)
os.environ["PROJ_LIB"] = str(RASTERIO_PROJ)
os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "EMPTY_DIR"
os.environ["CPL_VSIL_CURL_ALLOWED_EXTENSIONS"] = ".tif"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("APP_DATA_DIR", BASE_DIR)).resolve()
COG_FOLDER_PATH = DATA_DIR / "dades_cog"
MBTILES_FOLDER_PATH = DATA_DIR / "mbtiles"
GLYPHS_ZIP_PATH = DATA_DIR / "glyphs.zip"
