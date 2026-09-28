import os
import logging
import re
import sqlite3
import subprocess
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .email_service import send_email

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


def _validate_request(name: str, url: str) -> tuple[str, str]:
    # Elimina accents/diacritics (ñ->n, à->a...) abans de descartar caracters no ascii
    normalized = unicodedata.normalize("NFKD", name.lower())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    slug = re.sub(r"[^a-z0-9_-]+", "-", normalized).strip("-_")
    if not slug or len(slug) > 80:
        raise ValueError("El nom ha de contenir entre 1 i 80 caràcters vàlids")

    parsed = urllib.parse.urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != GEOFABRIK_HOST
        or parsed.port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
        or not parsed.path.lower().endswith(".osm.pbf")
    ):
        raise ValueError("La URL ha de ser un fitxer .osm.pbf de download.geofabrik.de")

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

    with opener.open(request, timeout=60) as response:
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


def process_map(
    name: str, url: str, task_id: str, email: str | None = None
) -> dict[str, str]:
    """Download a Geofabrik PBF and generate an MBTiles file with Planetiler."""
    try:
        slug, validated_url = _validate_request(name, url)
        mbtiles_dir = Path(os.environ.get("MBTILES_DIR", "/app/mbtiles")).resolve()
        schema_path = Path(
            os.environ.get("PLANETILER_SCHEMA", "/app/planetiler.yaml")
        ).resolve()
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

            subprocess.run(
                [
                    "java",
                    "-jar",
                    str(planetiler_jar),
                    "generate-custom",
                    f"--schema={schema_path}",
                    f"--output={generated_mbtiles}",
                    f"--osm_url={validated_url}",
                    f"--osm_local_path={pbf_path}",
                    "--force",
                    # --- NOUS PARÀMETRES PER A BAIXA RAM ---
                    "--nodemap-type=sortedtable",  # El mode més eficient per a zones petites/mitjanes
                    "--nodemap-storage=mmap",      # Aboca el mapa de nodes a fitxers mapejats en disc
                    "--storage=mmap",              # Força l'ús de mmap per a la resta d'estructures
                    "--threads=1",                 # Evita l'acumulació de feina en paral·lel a la RAM
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
                        ("description", f"Mapa offline de la regió {slug}"),
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
                    "No s'ha pogut generar el mapa",
                    f"La generació de '{name}' ha fallat. Identificador de la tasca: {task_id}.",
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
                "El mapa ja està disponible",
                f"La generació de '{name}' ha acabat correctament.\n\n"
                f"Descarrega el mapa (disponible durant 24 hores):\n{download_url}\n\n"
                f"Identificador de la tasca: {task_id}.",
            )
        except Exception:
            logger.exception(
                "No s'ha pogut enviar el correu de finalització de la tasca %s", task_id
            )

    return result
