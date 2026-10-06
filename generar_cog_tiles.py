"""Divideix els TIFF ja extrets en COG d'un grau per a països seleccionats."""

import argparse
import math
import os
import tempfile
from pathlib import Path

from osgeo import gdal, osr
import numpy as np

gdal.UseExceptions()

SOURCE_DIR = Path.home() / "Downloads/comprimits"
OUTPUT_DIR = Path(__file__).resolve().parent / "dades_cog_paisos"

# Rectangles aproximats (oest, sud, est, nord) per als territoris demanats.
# Inclou Canàries, Madeira, Açores, Còrsega, les Shetland i Bornholm.
TARGET_BOUNDS = (
    (-9.6, 35.5, 4.5, 44.2),  # Espanya continental i Balears
    (-18.5, 27.5, -13.0, 29.8),  # Canàries
    (-9.6, 36.8, -6.0, 42.2),  # Portugal continental
    (-17.4, 32.2, -16.1, 33.2),  # Madeira
    (-31.5, 36.8, -24.5, 40.2),  # Açores
    (-5.6, 41.3, 9.8, 51.2),  # França metropolitana i Còrsega
    (-8.7, 49.8, 2.1, 61.0),  # Regne Unit
    (6.5, 35.4, 18.6, 47.2),  # Itàlia
    (5.8, 47.2, 15.1, 55.1),  # Alemanya
    (2.4, 49.4, 6.5, 51.6),  # Bèlgica, inclòs Brussel·les
    (8.0, 54.5, 15.3, 58.0),  # Dinamarca, inclòs Bornholm
    (-25.0, 63.0, -13.0, 67.0),  # Islàndia
)


def tile_name(lat: int, lon: int) -> str:
    north_south = "N" if lat >= 0 else "S"
    east_west = "E" if lon >= 0 else "W"
    return f"{north_south}{abs(lat):02d}{east_west}{abs(lon):03d}_cog.tif"


def find_source_tiffs(source_dir: Path) -> list[Path]:
    """Retorna els TIFF ja descomprimits de la carpeta d'entrada."""
    tiffs = sorted(
        path
        for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".tif", ".tiff"}
    )
    if not tiffs:
        raise FileNotFoundError(f"No s'han trobat arxius .tif o .tiff a {source_dir}")
    return tiffs


def _tile_range(start: float, end: float, pixel_size: float) -> range:
    # Step inside the raster edge to avoid an extra tile from a tiny overlap.
    epsilon = abs(pixel_size)
    return range(math.floor(start + epsilon), math.ceil(end - epsilon))


def _intersects_target(lat: int, lon: int) -> bool:
    """Indica si la tessel·la d'un grau toca algun territori seleccionat."""
    return any(
        lon < east
        and lon + 1 > west
        and lat < north
        and lat + 1 > south
        for west, south, east, north in TARGET_BOUNDS
    )


def _has_nonzero_data(band: gdal.Band, tile_size: int = 512) -> bool:
    """Retorna si hi ha algun píxel vàlid diferent de zero."""
    for y in range(0, band.YSize, tile_size):
        height = min(tile_size, band.YSize - y)
        for x in range(0, band.XSize, tile_size):
            width = min(tile_size, band.XSize - x)
            values = band.ReadAsArray(x, y, width, height)
            mask = band.GetMaskBand().ReadAsArray(x, y, width, height)
            if np.any((mask != 0) & (values != 0)):
                return True
    return False


def generate_tiles(
    source_tiffs: list[Path], output_dir: Path
) -> tuple[int, int, int, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cog-mosaic-") as temporary_dir:
        vrt_path = Path(temporary_dir) / "mosaic.vrt"
        vrt = gdal.BuildVRT(str(vrt_path), [str(path) for path in source_tiffs])
        if vrt is None:
            raise RuntimeError("No s'ha pogut crear el mosaic VRT")

        spatial_reference = osr.SpatialReference()
        if (
            spatial_reference.ImportFromWkt(vrt.GetProjection()) != 0
            or not spatial_reference.IsGeographic()
        ):
            raise ValueError(
                "Els TIFF d'entrada han d'estar en coordenades geogràfiques"
            )

        transform = vrt.GetGeoTransform()
        pixel_width, pixel_height = transform[1], transform[5]
        if pixel_width <= 0 or pixel_height >= 0 or transform[2] or transform[4]:
            raise ValueError(
                "Geotransform no compatible amb una graella latitud/longitud"
            )

        width = round(1 / pixel_width)
        height = round(1 / abs(pixel_height))
        if (
            width < 1
            or height < 1
            or not math.isclose(width * pixel_width, 1, rel_tol=1e-6)
            or not math.isclose(height * abs(pixel_height), 1, rel_tol=1e-6)
        ):
            raise ValueError("Resolució del TIFF d'entrada invàlida")

        candidates = set()
        for source_path in source_tiffs:
            source = gdal.Open(str(source_path))
            if source is None:
                raise RuntimeError(f"No s'ha pogut obrir {source_path}")
            source_transform = source.GetGeoTransform()
            source_pixel_width, source_pixel_height = (
                source_transform[1],
                source_transform[5],
            )
            if (
                source_pixel_width <= 0
                or source_pixel_height >= 0
                or source_transform[2]
                or source_transform[4]
            ):
                raise ValueError(
                    f"Geotransform no compatible amb una graella latitud/longitud: "
                    f"{source_path}"
                )
            source_west, source_north = source_transform[0], source_transform[3]
            source_east = (
                source_west + source.RasterXSize * source_pixel_width
            )
            source_south = (
                source_north + source.RasterYSize * source_pixel_height
            )
            source_lons = _tile_range(
                source_west, source_east, source_pixel_width
            )
            source_lats = _tile_range(
                source_south, source_north, source_pixel_height
            )
            candidates.update(
                (lat, lon)
                for lat in source_lats
                for lon in source_lons
                if _intersects_target(lat, lon)
            )
            source = None

        made = skipped_empty = skipped_existing = removed_empty = 0
        for lat, lon in sorted(candidates):
            destination = output_dir / tile_name(lat, lon)
            if destination.exists():
                existing = gdal.Open(str(destination))
                if existing is None:
                    raise RuntimeError(
                        f"No s'ha pogut obrir la tessel·la existent {destination}"
                    )
                if _has_nonzero_data(existing.GetRasterBand(1)):
                    skipped_existing += 1
                    existing = None
                    continue
                existing = None
                destination.unlink()
                removed_empty += 1

            warped = gdal.Warp(
                "",
                vrt,
                format="MEM",
                outputBounds=(lon, lat, lon + 1, lat + 1),
                width=width,
                height=height,
                resampleAlg="bilinear",
            )
            if warped is None:
                raise RuntimeError(
                    f"No s'ha pogut generar la tessel·la {destination.name}"
                )

            if not _has_nonzero_data(warped.GetRasterBand(1)):
                skipped_empty += 1
                warped = None
                continue

            temporary_output = destination.with_name(f".{destination.stem}.tmp.tif")
            try:
                result = gdal.Translate(
                    str(temporary_output),
                    warped,
                    format="COG",
                    creationOptions=[
                        "COMPRESS=DEFLATE",
                        "BLOCKSIZE=256",
                        "OVERVIEWS=NONE",
                    ],
                )
                if result is None:
                    raise RuntimeError(
                        f"No s'ha pogut desar la tessel·la {destination.name}"
                    )
                result = None
                os.replace(temporary_output, destination)
            finally:
                temporary_output.unlink(missing_ok=True)
                warped = None
            made += 1

        vrt = None
    return made, skipped_empty, skipped_existing, removed_empty


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source_dir",
        nargs="?",
        type=Path,
        default=SOURCE_DIR,
        help=f"carpeta amb els TIFF ja descomprimits (per defecte: {SOURCE_DIR})",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        type=Path,
        default=OUTPUT_DIR,
        help=f"carpeta de sortida dels COG (per defecte: {OUTPUT_DIR})",
    )
    args = parser.parse_args()
    source_dir = args.source_dir.expanduser()
    output_dir = args.output_dir.expanduser()
    source_tiffs = find_source_tiffs(source_dir)
    made, skipped_empty, skipped_existing, removed_empty = generate_tiles(
        source_tiffs, output_dir
    )
    print(
        f"COG creats: {made}; mar/sense elevació omesos: {skipped_empty}; "
        f"ja vàlids existents omesos: {skipped_existing}; "
        f"COG buits antics eliminats: {removed_empty}"
    )
    print(f"Carpeta de sortida: {output_dir}")


if __name__ == "__main__":
    main()
