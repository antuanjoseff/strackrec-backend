import math
import os
import re

from .. import config
from ..footprint import build_footprint
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from rio_tiler.io import COGReader
import numpy as np

router = APIRouter()
_footprint_cache = None


def obtenir_ruta_local_cog(lat: float, lon: float) -> str:
    lat_tile, lon_tile = int(lat), int(lon)
    north_south = "N" if lat_tile >= 0 else "S"
    east_west = "E" if lon_tile >= 0 else "W"
    filename = f"{north_south}{abs(lat_tile):02d}{east_west}{abs(lon_tile):03d}_cog.tif"
    path = config.COG_FOLDER_PATH / filename

    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No es troba l'arxiu {filename}")

    return str(path)


@router.get("/getTile")
def get_tile(
    lat: float = Query(...), lon: float = Query(...), buf: float = Query(None)
):
    try:
        buffer = buf if buf is not None else 0.07
        ruta_fitxer_local = obtenir_ruta_local_cog(lat, lon)

        with COGReader(ruta_fitxer_local) as cog:
            img = cog.part(
                (lon - buffer, lat - buffer, lon + buffer, lat + buffer),
                width=500,
                height=500,
            )
            raw_data = img.data.astype(np.float32).tobytes()
            headers = {
                "Content-Disposition": f"attachment; filename={os.path.basename(ruta_fitxer_local)}.bin",
                "x-bbox": f"{lon-buffer},{lat-buffer},{lon+buffer},{lat+buffer}",
                "x-width": "500",
                "x-height": "500",
            }
            return Response(
                content=raw_data, media_type="application/octet-stream", headers=headers
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getTileGrid")
def get_tile_grid(lat: float = Query(...), lon: float = Query(...)):
    try:
        tile_lat = round(math.floor(lat / 0.2) * 0.2, 2)
        tile_lon = round(math.floor(lon / 0.2) * 0.2, 2)
        bbox = (tile_lon, tile_lat, round(tile_lon + 0.2, 2), round(tile_lat + 0.2, 2))
        ruta_fitxer_local = obtenir_ruta_local_cog(lat, lon)

        with COGReader(ruta_fitxer_local) as cog:
            img = cog.part(bbox)
            raw_data = img.data.astype(np.float32).tobytes()
            headers = {
                "Content-Disposition": f"attachment; filename=tile_{tile_lat}_{tile_lon}.bin",
                "x-bbox": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
                "x-width": str(img.width),
                "x-height": str(img.height),
            }
            return Response(
                content=raw_data, media_type="application/octet-stream", headers=headers
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/listTiles")
def list_tiles():
    try:
        pattern = re.compile(r"^[NS]\d{2}[EW]\d{3}_cog\.tif$")
        tiles = sorted(
            filename[: -len("_cog.tif")]
            for filename in os.listdir(config.COG_FOLDER_PATH)
            if pattern.match(filename)
        )
        return {"tiles": tiles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/footprint")
def get_footprint():
    global _footprint_cache
    if _footprint_cache is not None:
        return _footprint_cache

    try:
        pattern = re.compile(r"^[NS]\d{2}[EW]\d{3}_cog\.tif$")
        tiles = sorted(
            filename[: -len("_cog.tif")]
            for filename in os.listdir(config.COG_FOLDER_PATH)
            if pattern.match(filename)
        )
        _footprint_cache = build_footprint(tiles)
        return _footprint_cache
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
