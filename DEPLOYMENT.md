# Desplegament amb Docker

Aquesta aplicacio es pot executar en local o en produccio. El fitxer `docker-compose.yml` defineix els serveis base; `docker-compose.local.yml` nomes s'ha d'afegir per al desenvolupament local.

## Fitxers necessaris

Per construir les imatges cal tenir al repositori:

- `docker-compose.yml`
- `docker-compose.local.yml` per a local
- `Dockerfile`
- `Dockerfile.worker`
- `requirements.txt`
- `requirements-worker.txt`
- `main.py`
- la carpeta `strackrec_backend/`
- la carpeta `planetiler/`, amb `planetiler.yaml` i `planetiler.jar`

En produccio tambe cal tenir un fitxer d'entorn segur, per exemple:

```text
/etc/strackrec/production.env
```

Aquest fitxer no s'ha de pujar al repositori.

## Desplegament local

Des del directori del projecte:

```bash
source ./environment.sh
sudo -E docker compose \
  -f docker-compose.yml \
  -f docker-compose.local.yml \
  up -d --build --force-recreate
```

El fitxer `environment.sh` carrega les variables locals i demana la contrasenya SMTP si no existeix a l'entorn.

El fitxer `docker-compose.local.yml` modifica el compose base de la manera següent:

- publica l'API a `127.0.0.1:8000`;
- canvia `APP_PUBLIC_URL` a `http://localhost:8000`;
- munta `./dades_cog` i `./mbtiles` del repositori;
- munta `./main.py` dins del contenidor de l'API;
- utilitza una xarxa `webproxy` local, no externa.

Per comprovar l'estat:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.local.yml \
  ps
```

Per veure els logs:

```bash
sudo docker compose \
  -f docker-compose.yml \
  -f docker-compose.local.yml \
  logs -f api worker
```

L'API local queda disponible a:

```text
http://localhost:8000
```

## Desplegament en produccio

En produccio no cal executar `source environment.sh`. Docker Compose llegeix les variables del fitxer permanent amb `--env-file`.

Exemple de `/etc/strackrec/production.env`:

```env
SMTP_HOST=smtp.serviciodecorreo.es
SMTP_PORT=465
SMTP_USER=noreply@trackio.es
SMTP_PASSWORD=CONTRASENYA_SMTP
SMTP_FROM=noreply@trackio.es
SMTP_USE_SSL=true
SMTP_TIMEOUT_SECONDS=20

APP_PUBLIC_URL=https://trackio.es/api
CONFIRMATION_SECRET=SECRET_GENERAT_AMB_OPENSSL
REDIS_URL=redis://redis:6379/0

MBTILES_DIR=/app/mbtiles
PLANETILER_SCHEMA=/opt/planetiler/planetiler.yaml
PLANETILER_JAR=/opt/planetiler/planetiler.jar
PBF_MAX_DOWNLOAD_BYTES=21474836480
MBTILES_TTL_SECONDS=86400
MBTILES_CLEANUP_INTERVAL_SECONDS=3600
```

Protegeix el fitxer:

```bash
sudo chown root:root /etc/strackrec/production.env
sudo chmod 600 /etc/strackrec/production.env
```

Genera el secret de confirmacio amb:

```bash
openssl rand -hex 32
```

Abans de desplegar, valida la configuracio:

```bash
sudo docker compose \
  --env-file /etc/strackrec/production.env \
  -f docker-compose.yml \
  config >/dev/null
```

Reconstrueix les imatges i recrea tots els serveis:

```bash
sudo docker compose \
  --env-file /etc/strackrec/production.env \
  -f docker-compose.yml \
  up -d --build --force-recreate
```

Comprova l'estat:

```bash
sudo docker compose \
  --env-file /etc/strackrec/production.env \
  -f docker-compose.yml \
  ps
```

Consulta els logs:

```bash
sudo docker compose \
  --env-file /etc/strackrec/production.env \
  -f docker-compose.yml \
  logs -f api worker
```

## Requisits especifics de produccio

El `docker-compose.yml` actual espera:

- que existeixi la xarxa Docker externa `webproxy`;
- que existixin `/data/apps/mdt/dades_cog` i `/data/apps/mdt/mbtiles`;
- que Traefik utilitzi les xarxes i labels definides al compose;
- que el domini `trackio.es` apunti al servidor i Traefik gestioni HTTPS.

Si la xarxa `webproxy` encara no existeix, cal crear-la una vegada:

```bash
sudo docker network create webproxy
```

## Diferencia resumida

| Aspecte          | Local                                             | Produccio                              |
| ---------------- | ------------------------------------------------- | -------------------------------------- |
| Fitxers Compose  | `docker-compose.yml` + `docker-compose.local.yml` | nomes `docker-compose.yml`             |
| Variables        | `source environment.sh`                           | `/etc/strackrec/production.env`        |
| URL API          | `http://localhost:8000`                           | `https://trackio.es/api`               |
| API publicada    | port local `8000`                                 | Traefik i HTTPS                        |
| MBTiles          | `./mbtiles`                                       | `/data/apps/mdt/mbtiles`               |
| Xarxa `webproxy` | local, no externa                                 | externa i compartida amb Traefik       |
| Volums de codi   | inclou mounts locals                              | imatges construides amb el codi copiat |

No s'ha d'utilitzar `docker-compose.local.yml` en produccio, perquè canviaria els ports, els volums i la URL publica.
