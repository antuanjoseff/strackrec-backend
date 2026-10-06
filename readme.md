# Generació de rajoles de municipis amb Planetiler

Resum dels problemes trobats i les solucions aplicades en generar rajoles vectorials (MBTiles) a partir de `municipis_cat.geojson` amb Planetiler. L'esquema es troba a [planetiler/municipis.yaml](planetiler/municipis.yaml).

## 1. El conflicte del perfil d'OpenMapTiles (JAR bloquejat)

- **El problema:** Inicialment, Planetiler intentava descarregar gigabytes de dades globals (llacs, oceans, etc.) i es bloquejava si deies que no descarregués res.
- **El motiu:** El fitxer `planetiler.jar` és una versió modificada i precompilada específicament pel projecte OpenMapTiles que ignora els paràmetres de perfil simple comuns de Planetiler.
- **La solució:** Aquest JAR requereix la subcomanda obligatòria **`generate-custom`** per poder llegir fitxers d'esquema YAML personals i saltar-se el mapa base del món.

## 2. Errors de sintaxi i el parser de Jackson (YAML invàlid)

- **El problema:** El programa llançava un error Java de tipus `UnrecognizedPropertyException` o `MismatchedInputException` i es tancava abans de fer res.
- **El motiu:** S'utilitzaven paràmetres de l'esquema estàndard de Planetiler (com `schema:`, `include_all_attributes` o estructures de claus/valors directes a la capa). El motor del JAR és molt exigent i només accepta 4 propietats d'arrel, i obliga a posar tota la configuració de zooms i dades dins del bloc de llista **`features:`**.
- **La solució:** Simplificar el YAML a la seva estructura mínima i plana, eliminant els blocs d'esquema i binaris que feien fallar el lector Jackson.

## 3. Rutes de Windows i fitxers ocults de macOS

- **El problema:** Planetiler deia que el fitxer GeoJSON d'origen no existia a la ruta especificada.
- **El motiu:** Windows duplica o altera els caràcters de les rutes absolutes (`:`, `\`) quan es passen per consola, i a més el sistema intentava llegir un fitxer ocult de metadades de macOS (`._municipis_cat.geojson`) en lloc del GeoJSON net.
- **La solució:** Moure el fitxer manualment a la carpeta interna de dependències de Planetiler (`data/sources/`) i definir una **ruta 100% relativa** al YAML (`url: municipis_cat.geojson`).

## 4. Arxiu buit (rajoles de 20 KB) o transparent

- **El problema:** El procés acabava correctament però l'arxiu resultant pesava només 20 KB (buit), o feia 1 MB però a QGIS no es veia res.
- **El motiu:** Sense filtres de geometria definits, Planetiler creava l'estructura del mapa però no escrivia cap polígon dins de les rajoles. A més, en no especificar `geometry: polygon`, QGIS interpretava les geometries com a desconegudes i no sabia com pintar-les.
- **La solució:** Aplicar la configuració reduïda (vegeu l'YAML), que fa pujar el pes a **1 MB**, indicant clarament el rang de zooms de visualització (6 a 11) i `geometry: polygon`.
