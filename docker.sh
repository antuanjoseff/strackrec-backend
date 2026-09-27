# Iniciar el docker en local
source ./environment.sh
sudo -E docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build --force-recreate api

#  Comprovar el confirmation secret
sudo -E docker compose -f docker-compose.yml -f docker-compose.local.yml exec -T api sh -lc 'test -n "$CONFIRMATION_SECRET" && echo "Secret configurat" || echo "FALTA el secret"'

# Fer el build en local
sudo docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build

# Aixecar en local
docker compose -f docker-compose.yml -f docker-compose.local.yml ps

# build i aixecar en local
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build --force-recreate api

# Comprovar
docker compose -f docker-compose.yml -f docker-compose.local.yml ps

# prova url mbtiles bboxes
curl -i http://localhost:8000/mapes/bounds.geojson

# Enviar peticio post 
curl -i -X POST http://localhost:8000/mapes/requests \
  -H 'Content-Type: application/json' \
  -d '{"name":"Catalunya","url":"https://download.geofabrik.de/europe/spain/catalunya-lastest.osm.pbf","email":"tonidelacalle@gmail.com"}'

curl -i -X POST http://localhost:8000/mapes/requests \
  -H 'Content-Type: application/json' \
  -d '{"name":"Corse","url":"https://download.geofabrik.de/europe/france/corse-latest.osm.pbf","email":"tonidelacalle@gmail.com"}'

curl -i -X POST http://localhost:8000/mapes/requests \
  -H 'Content-Type: application/json' \
  -d '{"name":"La Rioja","url":"https://download.geofabrik.de/europe/spain/la-rioja-latest.osm.pbf","email":"tonidelacalle@gmail.com"}'


curl -i -X POST https://trackio.es/api/mapes/requests \
  -H 'Content-Type: application/json' \
  -d '{"name":"La Rioja","url":"https://download.geofabrik.de/europe/spain/la-rioja-latest.osm.pbf","email":"tonidelacalle@gmail.com"}'


# amb lang : it
curl -i -X POST http://localhost:8000/mapes/requests \
  -H 'Content-Type: application/json' \
  -d '{"name":"Catalunya","url":"https://download.geofabrik.de/europe/spain/cataluna-latest.osm.pbf","email":"tonidelacalle@gmail.com","lang":"ca"}'

curl -i -X POST http://localhost:8000/mapes/requests \
  -H 'Content-Type: application/json' \
  -d '{"name":"Corse","url":"https://download.geofabrik.de/europe/france/corse-latest.osm.pbf","email":"tonidelacalle@gmail.com","lang":"es"}'

# Comprova l'estat d'una tasca
sudo docker compose -f docker-compose.yml -f docker-compose.local.yml exec -T worker python -c 'from redis import Redis; from rq.job import Job; c=Redis.from_url("redis://redis:6379/0"); j=Job.fetch("04b3cdfbb58c45a2b3dec8c11c720d8a", connection=c); print(j.exc_info or "No hi ha traceback guardat")'

#   Mes comandes
sudo -E docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --force-recreate api
sudo docker compose -f docker-compose.yml -f docker-compose.local.yml exec -T api sh -lc 'test -n "$CONFIRMATION_SECRET" && echo "Secret configurat" || echo "FALTA el secret"'
