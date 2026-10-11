import http.client
import json
import math
import time
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

GEOFABRIK_INDEX_URL = "https://download.geofabrik.de/index-v1.json"
CACHE_TTL_SECONDS = 6 * 60 * 60
_cache = {"expires": 0.0, "content": None}


def _coordinate_pairs(coordinates):
    if isinstance(coordinates, list):
        if (
            len(coordinates) >= 2
            and isinstance(coordinates[0], (int, float))
            and isinstance(coordinates[1], (int, float))
        ):
            yield coordinates[0], coordinates[1]
        else:
            for item in coordinates:
                yield from _coordinate_pairs(item)


def _feature_bbox(feature):
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict):
        raise ValueError("Feature sense geometria vàlida")

    coordinates = geometry.get("coordinates")
    points = _coordinate_pairs(coordinates)
    first_point = next(points, None)
    if first_point is None:
        raise ValueError("Geometria sense coordenades vàlides")

    west, south = east, north = first_point
    for longitude, latitude in points:
        west = min(west, longitude)
        south = min(south, latitude)
        east = max(east, longitude)
        north = max(north, latitude)

    bbox = [west, south, east, north]
    if not all(math.isfinite(value) for value in bbox):
        raise ValueError("Geometria amb coordenades no finites")
    return bbox


@router.get("/geofabrik/regions")
def obtenir_regions_geofabrik():
    if _cache["content"] is not None and time.monotonic() < _cache["expires"]:
        return JSONResponse(
            content=_cache["content"], media_type="application/geo+json"
        )
    try:
        with urlopen(GEOFABRIK_INDEX_URL, timeout=30) as response:
            collection = json.load(response)

        features = collection.get("features")
        if not isinstance(features, list):
            raise ValueError("La resposta no conté una llista de features")

        parent_ids = {
            feature.get("properties", {}).get("parent")
            for feature in features
            if isinstance(feature, dict)
            and isinstance(feature.get("properties"), dict)
            and isinstance(feature.get("properties", {}).get("parent"), str)
        }

        leaf_features = []
        for feature in features:
            if not isinstance(feature, dict):
                raise ValueError("Feature no vàlida")
            properties = feature.get("properties")
            if not isinstance(properties, dict):
                raise ValueError("Feature sense propietats vàlides")
            if properties.get("id") in parent_ids:
                continue

            try:
                bbox = _feature_bbox(feature)
            except ValueError:
                continue

            leaf_features.append(
                {
                    "type": "Feature",
                    "bbox": bbox,
                    "properties": properties,
                }
            )

        content = {"type": "FeatureCollection", "features": leaf_features}
        _cache["expires"] = time.monotonic() + CACHE_TTL_SECONDS
        _cache["content"] = content
        return JSONResponse(content=content, media_type="application/geo+json")
    except (
        URLError,
        OSError,
        http.client.HTTPException,
        json.JSONDecodeError,
        ValueError,
    ) as error:
        raise HTTPException(
            status_code=502,
            detail=f"No s'ha pogut obtenir l'índex de Geofabrik: {error}",
        ) from error
