import math
import re
import sqlite3

from .. import config
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter()


@router.get("/mapes/glyphs/")
@router.get("/mapes/glyphs")
def descarregar_glyphs():
    """Serveix el paquet de glyphs compartit per les regions offline."""
    ruta_zip = config.GLYPHS_ZIP_PATH
    if not ruta_zip.exists():
        raise HTTPException(
            status_code=404,
            detail="El paquet de glyphs no està disponible al servidor.",
        )

    headers = {"Content-Disposition": "attachment; filename=glyphs.zip"}
    return FileResponse(
        path=ruta_zip, media_type="application/octet-stream", headers=headers
    )


@router.get("/mapes/bounds.geojson")
def obtenir_bounds_mapes():
    try:
        features = []
        fitxers = sorted(
            (
                path
                for path in config.MBTILES_FOLDER_PATH.iterdir()
                if path.is_file() and path.suffix.lower() == ".mbtiles"
            ),
            key=lambda path: path.name,
        )

        for path in fitxers:
            filename = path.name
            try:
                database_uri = f"{path.resolve().as_uri()}?mode=ro"
                with sqlite3.connect(database_uri, uri=True) as conn:
                    metadata = dict(conn.execute("SELECT name, value FROM metadata"))
            except sqlite3.Error as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"No s'han pogut llegir les metadades de {filename}",
                ) from e

            bounds_value = metadata.get("bounds")
            if bounds_value is None:
                raise HTTPException(
                    status_code=500,
                    detail=f"El fitxer {filename} no conté metadades bounds",
                )

            try:
                bounds = [float(value) for value in bounds_value.split(",")]
            except (AttributeError, ValueError) as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Les metadades bounds de {filename} no són vàlides",
                ) from e

            if (
                len(bounds) != 4
                or not all(math.isfinite(value) for value in bounds)
                or bounds[0] > bounds[2]
                or bounds[1] > bounds[3]
                or not (-180 <= bounds[0] <= bounds[2] <= 180)
                or not (-90 <= bounds[1] <= bounds[3] <= 90)
            ):
                raise HTTPException(
                    status_code=500,
                    detail=f"Les metadades bounds de {filename} no són vàlides",
                )

            west, south, east, north = bounds
            name = path.stem
            properties = {
                **metadata,
                "filename": filename,
                "file_size_bytes": path.stat().st_size,
                "description": f"Mapa offline de la regió {name}",
            }
            features.append(
                {
                    "type": "Feature",
                    "id": name,
                    "properties": properties,
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [west, south],
                                [east, south],
                                [east, north],
                                [west, north],
                                [west, south],
                            ]
                        ],
                    },
                }
            )

        return JSONResponse(
            content={"type": "FeatureCollection", "features": features},
            media_type="application/geo+json",
            headers={
                "Content-Disposition": 'attachment; filename="mapes-bounds.geojson"'
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mapes/{regio}")
def descarregar_mapa_offline(regio: str):
    """Descarrega un fitxer MBTiles per a ús offline."""
    if not re.fullmatch(r"[a-z0-9_\-]+", regio.lower()):
        raise HTTPException(status_code=400, detail="Nom de regió no vàlid")

    nom_fitxer = f"{regio.lower()}.mbtiles"
    ruta_fitxer_mbtiles = config.MBTILES_FOLDER_PATH / nom_fitxer
    if not ruta_fitxer_mbtiles.exists():
        raise HTTPException(
            status_code=404,
            detail=f"El mapa offline de la regió '{regio}' no està disponible al servidor.",
        )

    headers = {"Content-Disposition": f"attachment; filename={nom_fitxer}"}
    return FileResponse(
        path=ruta_fitxer_mbtiles,
        media_type="application/octet-stream",
        headers=headers,
    )
