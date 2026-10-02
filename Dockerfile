# =========================================================
# FASE 1: Agafem la imatge oficial de Tippecanoe com a font
# =========================================================
FROM axismaps/tippecanoe:latest AS tippecanoe_source

# =========================================================
# FASE 2: La teva imatge actual de FastAPI
# =========================================================
FROM python:3.12-slim

WORKDIR /app

# 1. Instal·lem les teves llibreries geoespacials de sistema actuals
RUN apt-get update && apt-get install -y \
    libexpat1 \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. TRUC MÀGIC: Copiem el binari ja compilat de Tippecanoe des de la Fase 1
COPY --from=tippecanoe_source /usr/local/bin/tippecanoe /usr/local/bin/tippecanoe
COPY --from=tippecanoe_source /usr/local/bin/tile-join /usr/local/bin/tile-join

# 3. Seguim amb la teva instal·lació habitual de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
