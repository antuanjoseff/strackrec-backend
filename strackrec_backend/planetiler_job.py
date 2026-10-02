import os
import logging
import math
import re
import sqlite3
import subprocess
import struct
import tempfile
import unicodedata
import zlib
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .email_service import send_email
from .translations import DEFAULT_LANGUAGE, Lang, get_texts

GEOFABRIK_HOST = "download.geofabrik.de"
DEFAULT_MAX_DOWNLOAD_BYTES = 20 * 1024**3
logger = logging.getLogger(__name__)


class GeofabrikRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlparse(newurl)
        if (
            parsed.scheme != "https"
            or parsed.hostname != GEOFABRIK_HOST
            or parsed.port not in (None, 443)
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise urllib.error.HTTPError(
                newurl, code, "Redirect to an untrusted host refused", headers, fp
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _validate_request(
    name: str, url: str, lang: Lang = DEFAULT_LANGUAGE
) -> tuple[str, str]:
    texts = get_texts(lang)
    # Elimina accents/diacritics (ñ->n, à->a...) abans de descartar caracters no ascii
    normalized = unicodedata.normalize("NFKD", name.lower())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    slug = re.sub(r"[^a-z0-9_-]+", "-", normalized).strip("-_")
    if not slug or len(slug) > 80:
        raise ValueError(texts["invalid_map_name"])

    parsed = urllib.parse.urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != GEOFABRIK_HOST
        or parsed.port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
        or not parsed.path.lower().endswith(".osm.pbf")
    ):
        raise ValueError(texts["invalid_map_url"])

    return slug, url


def _download_pbf(url: str, destination: Path) -> None:
    max_bytes = int(
        os.environ.get("PBF_MAX_DOWNLOAD_BYTES", DEFAULT_MAX_DOWNLOAD_BYTES)
    )
    opener = urllib.request.build_opener(GeofabrikRedirectHandler())
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "strackrec-backend/1.0"},
    )

    with opener.open(request, timeout=300) as response:
        content_length = response.headers.get("Content-Length")
        if content_length is not None and int(content_length) > max_bytes:
            raise ValueError("El fitxer PBF supera la mida màxima permesa")

        downloaded = 0
        with destination.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                downloaded += len(chunk)
                if downloaded > max_bytes:
                    raise ValueError("El fitxer PBF supera la mida màxima permesa")
                output.write(chunk)


def _proto_fields(data: bytes):
    """Itera (camp, valor) d'un missatge protobuf; valor es int o bytes."""
    pos = 0
    while pos < len(data):
        key = shift = 0
        while True:
            b = data[pos]
            pos += 1
            key |= (b & 0x7F) << shift
            shift += 7
            if not b & 0x80:
                break
        field, wire = key >> 3, key & 7
        if wire == 0:
            value = shift = 0
            while True:
                b = data[pos]
                pos += 1
                value |= (b & 0x7F) << shift
                shift += 7
                if not b & 0x80:
                    break
            yield field, value
        elif wire == 2:
            length = shift = 0
            while True:
                b = data[pos]
                pos += 1
                length |= (b & 0x7F) << shift
                shift += 7
                if not b & 0x80:
                    break
            yield field, data[pos : pos + length]
            pos += length
        elif wire == 1:
            pos += 8
        elif wire == 5:
            pos += 4
        else:
            raise ValueError("Wire type protobuf no suportat")


def _pbf_bbox(pbf_path: Path) -> tuple[float, float, float, float] | None:
    """Retorna (oest, sud, est, nord) de la capcalera del PBF, o None."""
    with pbf_path.open("rb") as f:
        header_len = struct.unpack(">I", f.read(4))[0]
        datasize = 0
        for field, value in _proto_fields(f.read(header_len)):
            if field == 3:
                datasize = value
        blob = f.read(datasize)

    raw = None
    for field, value in _proto_fields(blob):
        if field == 1:
            raw = value
        elif field == 3:
            raw = zlib.decompress(value)
    if raw is None:
        return None

    def unzigzag(n: int) -> int:
        return (n >> 1) ^ -(n & 1)

    for field, value in _proto_fields(raw):
        if field == 1:
            box = {f: unzigzag(v) / 1e9 for f, v in _proto_fields(value)}
            if {1, 2, 3, 4} <= box.keys():
                return box[1], box[4], box[2], box[3]
    return None


def _generate_contours(
    pbf_path: Path, cog_dir: Path, work_dir: Path, interval: int = 20
) -> Path | None:
    """Genera un GeoPackage de corbes de nivell amb l'extensio del PBF.

    Retorna None si no hi ha COGs que cobreixin la zona.
    """
    if not cog_dir.is_dir():
        return None
    bbox = _pbf_bbox(pbf_path)
    if bbox is None:
        logger.warning("El PBF no conte bbox a la capcalera; sense corbes")
        return None
    west, south, east, north = bbox

    # Els COG son tessel·les d'1x1 graus anomenades per la cantonada SW (N42E002).
    tiles = []
    for lat in range(math.floor(south), math.ceil(north)):
        for lon in range(math.floor(west), math.ceil(east)):
            ns = "N" if lat >= 0 else "S"
            ew = "E" if lon >= 0 else "W"
            tile = cog_dir / f"{ns}{abs(lat):02d}{ew}{abs(lon):03d}_cog.tif"
            if tile.is_file():
                tiles.append(tile)
    if not tiles:
        logger.info("Sense COGs per a la zona; es genera sense corbes")
        return None

    list_file = work_dir / "cogs.txt"
    list_file.write_text("\n".join(str(t) for t in tiles))
    vrt = work_dir / "cogs.vrt"
    cropped = work_dir / "cropped.vrt"
    gpkg = work_dir / "corbes.gpkg"
    subprocess.run(
        ["gdalbuildvrt", "-input_file_list", str(list_file), str(vrt)], check=True
    )
    subprocess.run(
        [
            "gdal_translate",
            "-of",
            "VRT",
            "-projwin",
            str(west),
            str(north),
            str(east),
            str(south),
            str(vrt),
            str(cropped),
        ],
        check=True,
    )
    subprocess.run(
        [
            "gdal_contour",
            "-i",
            str(interval),
            "-a",
            "ele",
            "-f",
            "GPKG",
            "-nln",
            "contour",
            str(cropped),
            str(gpkg),
        ],
        check=True,
    )
    return gpkg if gpkg.is_file() else None


def process_map(
    name: str,
    url: str,
    task_id: str,
    email: str | None = None,
    lang: Lang = DEFAULT_LANGUAGE,
) -> dict[str, str]:
    """Download a Geofabrik PBF and generate an MBTiles file with Planetiler."""
    texts = get_texts(lang)
    try:
        slug, validated_url = _validate_request(name, url, lang)
        mbtiles_dir = Path(os.environ.get("MBTILES_DIR", "/app/mbtiles")).resolve()
        schema_path = Path(
            os.environ.get("PLANETILER_SCHEMA", "/app/planetiler.yaml")
        ).resolve()
        contour_schema_path = Path(
            os.environ.get(
                "PLANETILER_CONTOUR_SCHEMA", "/opt/planetiler/planetiler-corbes.yaml"
            )
        ).resolve()
        cog_dir = Path(os.environ.get("COG_DIR", "/app/dades_cog")).resolve()
        planetiler_jar = Path(
            os.environ.get("PLANETILER_JAR", "/opt/planetiler/planetiler.jar")
        ).resolve()

        if not schema_path.is_file():
            raise FileNotFoundError(f"No es troba l'esquema Planetiler: {schema_path}")
        if not planetiler_jar.is_file():
            raise FileNotFoundError(f"No es troba Planetiler: {planetiler_jar}")

        mbtiles_dir.mkdir(parents=True, exist_ok=True)
        output_name = f"{slug}-{task_id[:8]}.mbtiles"
        final_output = mbtiles_dir / output_name

        with tempfile.TemporaryDirectory(
            prefix=f".planetiler-{task_id[:8]}-", dir=mbtiles_dir
        ) as temp_dir:
            temp_path = Path(temp_dir)
            pbf_path = temp_path / "input.osm.pbf"
            generated_mbtiles = temp_path / "output.mbtiles"
            _download_pbf(validated_url, pbf_path)

            contours = None
            if contour_schema_path.is_file():
                try:
                    contours = _generate_contours(pbf_path, cog_dir, temp_path)
                except Exception:
                    logger.exception("Error generant corbes; es continua sense")

            active_schema = contour_schema_path if contours else schema_path
            extra_args = [f"--corbes_local_path={contours}"] if contours else []

            subprocess.run(
                [
                    "java",
                    "-jar",
                    str(planetiler_jar),
                    "generate-custom",
                    f"--schema={active_schema}",
                    *extra_args,
                    f"--output={generated_mbtiles}",
                    f"--osm_url={validated_url}",
                    f"--osm_local_path={pbf_path}",
                    "--force",
                    # --- NOUS PARÀMETRES PER A BAIXA RAM ---
                    "--nodemap-type=sortedtable",  # El mode més eficient per a zones petites/mitjanes
                    "--nodemap-storage=mmap",  # Aboca el mapa de nodes a fitxers mapejats en disc
                    "--storage=mmap",  # Força l'ús de mmap per a la resta d'estructures
                    "--threads=1",  # Evita l'acumulació de feina en paral·lel a la RAM
                    "--workers=1",
                ],
                check=True,
                cwd=temp_dir,
            )

            if not generated_mbtiles.is_file():
                raise RuntimeError(
                    "Planetiler ha acabat sense generar el fitxer MBTiles"
                )
            file_size_bytes = generated_mbtiles.stat().st_size
            with sqlite3.connect(generated_mbtiles) as conn:
                conn.executemany(
                    "INSERT OR REPLACE INTO metadata (name, value) VALUES (?, ?)",
                    [
                        ("name", slug),
                        (
                            "description",
                            texts["generated_map_description"].format(name=slug),
                        ),
                        ("file_size_bytes", str(file_size_bytes)),
                    ],
                )
            os.replace(generated_mbtiles, final_output)

        result = {"filename": output_name, "path": str(final_output)}
    except Exception:
        if email:
            try:
                send_email(
                    email,
                    texts["map_generation_failed_subject"],
                    texts["map_generation_failed_body"].format(
                        name=name, task_id=task_id
                    ),
                )
            except Exception:
                logger.exception(
                    "No s'ha pogut enviar l'avís de fallada de la tasca %s", task_id
                )
        raise

    if email:
        public_url = os.environ.get("APP_PUBLIC_URL", "https://trackio.es/api").rstrip(
            "/"
        )
        download_url = f"{public_url}/mapes/{Path(result['filename']).stem}"
        try:
            send_email(
                email,
                texts["map_generation_ready_subject"],
                texts["map_generation_ready_body"].format(
                    name=name, download_url=download_url, task_id=task_id
                ),
            )
        except Exception:
            logger.exception(
                "No s'ha pogut enviar el correu de finalització de la tasca %s", task_id
            )

    return result
