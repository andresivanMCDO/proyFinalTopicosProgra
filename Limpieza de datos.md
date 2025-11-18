# Obtención del dataset
Para la realización de este proyecto se empleó un dataset solicitado a la GBIF (Global Biodiversity Information Facility) que es una red internacional que mantiene una base de datos de la biodiversidad del planeta, alimentándose de diversas instituciones como la CONABIO, la UNAM, universidades y gobiernos de distintos países que colaboran agregando los avistamientos u observaciones que han hecho por distintos medios (por ejemplo exploración de campo o mediante monitoreo con cámaras) registrando información relevante como fecha, hora, nombre científico, número de ejemplares, coordenadas, etc.
A través de su página www.gbif.org se hizo una solicitud de información con las siguientes características en formato CSV, además a este dataset tiene un DOI asociado que es https://doi.org/10.15468/dl.752wz3
``` json
{
 "and" : [ 
 "Country is Mexico", 
 "OccurrenceStatus is Present", 
 "TaxonKey is Leporidae" ] 
}
```
Ya que realizar un análisis de la totalidad de las formas de vida en el territorio nacional requeriría de mayores capacidades de cómputo y un mayor tiempo de espera a que la GBIF pueda proporcionarla(ya que la petición puede tomar desde unos cuantos minutos hasta horas) se tomó una porción de la totalidad de la biodiversidad. A continuación se muestra la porción del arbol taxonómico que se tomó y el número de observaciones de cada sección, más específicamente se escogió la familia *Leporidae* que contiene múltiples géneros, siendo los más observados *Sylvilagus*, *Lepus* y *Romerolagus*. El dataset como lo proporciona GBIF contiene 23,700 registros
```json
Reino
└─ Animalia............................................. 890,355
   Filo
   └─ Chordata....................................... 26,432,409
      Clase
      └─ Mammalia...................................... 890,355
         Orden
         └─ Lagomorpha................................... 23,786
            Familia
            └─ Leporidae................................ 23,672
               Géneros
               ├─ Sylvilagus.............................. 14,803
               ├─ Lepus.................................... 8,136
               ├─ Romerolagus.................................451
               ├─ Oryctolagus..................................61
               ├─ Hypolagus....................................50
               ├─ Notolagus....................................16
               ├─ Aztlanolagus.................................10
               ├─ Paranotolagus..................................9
               ├─ Pewelagus......................................6
               ├─ Aluralagus.....................................4
               ├─ Pratilepus.....................................4
               ├─ Pronotolagus....................................2
               └─ Unknown genus.................................. 148
	        Unknown family..................................... 86
```
El dataset proporcionado tiene también su diccionario de datos en la página https://techdocs.gbif.org/en/data-use/download-formats en el cual se observa que cuenta con 50 columnas, de las cuales para nuestro estudio escogeremos las 8 que nos son relevantes y cuyo diccionario de datos se anexa a continuación.

| Column name            | Data type | Nullable | Definition                                                                                                                                                                                                                  | Standard |
| ---------------------- | --------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| verbatimScientificName | String    | Yes      | Scientific name as provided by the source.                                                                                                                                                                                  | GBIF     |
| locality               | String    | Yes      | The specific description of the place.                                                                                                                                                                                      | DWC      |
| stateProvince          | String    | Yes      | The name of the next-smaller administrative region than country (state, province, canton, department, region, etc.) in which the occurrence occurs. This value is unaltered by GBIF’s processing; see also the GADM fields. | GBIF     |
| decimalLatitude        | Double    | Yes      | The geographic latitude (in decimal degrees, using the WGS84 datum) of the geographic centre of the location of the occurrence.                                                                                             | GBIF     |
| decimalLongitude       | Double    | Yes      | The geographic longitude (in decimal degrees, using the WGS84 datum) of the geographic centre of the location of the occurrence.                                                                                            | GBIF     |
| eventDate              | String    | Yes      | The date-time or interval during which a dwc:Event occurred. For occurrences, this is the date-time when the dwc:Event was recorded. Not suitable for a time in a geological context.                                       | DWC      |
| basisOfRecord          | String    | Yes      | The values of the Darwin Core term Basis of Record which can apply to occurrences. See GBIF’s Darwin Core Type Vocabulary for definitions.                                                                                  | GBIF     |
| institutionCode        | String    | Yes      | The name (or acronym) in use by the institution having custody of the object(s) or information referred to in the record.                                                                                                   | DWC      |
**Tabla 1.** Diccionario de datos que se conservan al final.
# Eliminación de columnas irrelevantes y justificación
## Columnas con gran porcentaje de nulos
Con el siguiente código se puede visualizar rápidamente cuál es el porcentaje de valores nulos por cada una de las 50 columnas
``` python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Cálculo de porcentajes de valores faltantes
missing = observaciones.isnull().mean().sort_values(ascending=False) * 100

# === SOLO LA GRÁFICA EN JUPYTER ===
fig, ax = plt.subplots(figsize=(10, 5))

# Filtrar solo las variables que sí tienen valores faltantes
missing_nonzero = missing[missing > 0]

if not missing_nonzero.empty:
    sns.barplot(
        x=missing_nonzero.values,
        y=missing_nonzero.index,
        hue=missing_nonzero.index,   # ← requerido para usar palette
        legend=False,                # ← evita mostrar una leyenda duplicada
        dodge=False,                 # ← necesario para evitar desplazamiento
        palette="viridis",
        height=0.8,                  # <--- ajusta espacio entre etiquetas
        ax=ax
    )
    ax.set_title("Gráfica de variables con valores faltantes")
    ax.set_xlabel("% de valores faltantes")
    ax.set_ylabel("Variable")
    plt.show()
else:
    print("No hay valores faltantes en el DataFrame.")
```

Obsérvese cómo 14 de las 50 columnas tienen un porcentaje de valores nulos mayor o igual al 40%, esas serán las primeras columnas en ser eliminadas(y que también están ligeramente sombreadas), quedándose solamente 36 de 50 columnas en esta primera etapa de filtrado
![Gráfica de valores faltantes](figures/fig_1_valores_faltantes.png)
**Figura 1.** Porcentaje de valores faltantes por variable.

| Variable                         | Porcentaje_Faltante | Variable               | Porcentaje_Faltante |
| -------------------------------- | ------------------- | ---------------------- | ------------------- |
| coordinatePrecision              | 99.52               | catalogNumber          | 7.84                |
| establishmentMeans               | 96.46               | recordedBy             | 7.78                |
| recordNumber                     | 89.87               | speciesKey             | 6.02                |
| dateIdentified                   | 77.15               | species                | 6.02                |
| mediaType                        | 75.05               | occurrenceID           | 3.49                |
| infraspecificEpithet             | 74.31               | issue                  | 1.93                |
| individualCount                  | 58.08               | stateProvince          | 1.88                |
| depthAccuracy                    | 55.95               | verbatimScientificName | 0.73                |
| depth                            | 55.95               | genus                  | 0.63                |
| typeStatus                       | 54.38               | countryCode            | 0                   |
| coordinateUncertaintyInMeters    | 51.31               | scientificName         | 0                   |
| elevationAccuracy                | 50.71               | taxonRank              | 0                   |
| verbatimScientificNameAuthorship | 49.29               | kingdom                | 0                   |
| elevation                        | 47.67               | class                  | 0                   |
| collectionCode                   | 28.59               | phylum                 | 0                   |
| rightsHolder                     | 27.83               | family                 | 0                   |
| identifiedBy                     | 27.59               | order                  | 0                   |
| day                              | 23.92               | gbifID                 | 0                   |
| month                            | 22.86               | datasetKey             | 0                   |
| year                             | 22.34               | publishingOrgKey       | 0                   |
| locality                         | 21.97               | occurrenceStatus       | 0                   |
| eventDate                        | 21.49               | taxonKey               | 0                   |
| institutionCode                  | 20.12               | basisOfRecord          | 0                   |
| decimalLatitude                  | 17.47               | license                | 0                   |
| decimalLongitude                 | 17.47               | lastInterpreted        | 0                   |
**Tabla 2.** Porcentaje de valores faltantes por variable.

Con el siguiente código se obtiene este primer paso de eliminar estas 14 columnas
```python
threshold = 40
observaciones = observaciones.loc[:, observaciones.isnull().mean() < (threshold / 100)]
```
## Columnas con información irrelevante
El siguiente paso es eliminar las columnas que, a pesar de tener un porcentaje de valores nulos menor a 40%, siguen sin ser relevantes para el análisis que se hará, eliminando otras 28 columnas; La justificación para eliminarlas es que por ejemplo las que terminan en key son claves que se serían requeridas en un contexto donde la integridad y cohesión relacional es clave y algunas de estas keys podrían ser útiles si, por ejemplo, fuera una cantidad mucho mayor de registros y se empleara una estructura apropiada para análisis más ambicioso empleando por ejemplo un modelo estrella con su tabla de hechos y dimensiones con los datos desnormalizados para facilitar el cómputo, pero ya que no es el caso, se prescinde de las columnas que son keys. 
Solo podría conservarse el `gbifID` pero de acuerdo a la GBIF en https://techdocs.gbif.org/en/data-use/download-formats "We aim to keep these keys stable, but this is not possible in every case." de manera que si se busca tener una llave primaria de valores únicos (PK & Unique values quizá autoincrementable) esta no funcionaría si se busca una integridad robusta, resulta más conveniente para nuestros objetivos crear un índice nuevo con la librería pandas.
Hay otras columnas como `datasetKey` o `publishingOrgKey` que son indicadores administrativos que corresponden con información de los proveedores de la información como universidades e instituciones de gobierno, pero la columna `institutionCode`ya brinda esta información

En la siguiente tabla se justifica la eliminación de cada una de estas columnas

| Columna eliminada    | Justificación                                                                                                                         |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **gbifID**           | No es una llave primaria robusta que garantice unicidad                                                                               |
| **datasetKey**       | Identificador técnico de la institución que hizo la observación, el institutionCode muestra mejor esta información.                   |
| **occurrenceID**     | Identificador interno de la ocurrencia; inconsistente entre instituciones y poco útil para el análisis ecológico.                     |
| **kingdom**          | Todos los registros pertenecen al mismo reino Animalia                                                                                |
| **phylum**           | Ya se sabe que el estudio se centra en el filo Chordata                                                                               |
| **class**            | El filo contiene a la clase Mammalia                                                                                                  |
| **order**            | El orden Lagomorpha es común a todos por el mismo motivo                                                                              |
| **family**           | Todos los registros tienen por familia Leporidae                                                                                      |
| **genus**            | Si bien el género es relevante, ya viene incluido en la columna verbatimScientificName                                                |
| **species**          | La misma columna verbatimScientificName ya contiene la especie                                                                        |
| **taxonRank**        | Si se trata de una especie o una subespecie se puede intuir con verbatimScientificName                                                |
| **scientificName**   | Es como verbatimScientificName pero con información del primer descubridor, e.g. (J.A.Allen, 1890) que para el estudio no se requiere |
| **countryCode**      | Toda la información es de México                                                                                                      |
| **occurrenceStatus** | Se asume que todos los registros son de presencia, por lo que es constante.                                                           |
| **publishingOrgKey** | Identificador interno del proveedor; irrelevante para los análisis.                                                                   |
| **day**              | Puede extraerse de la columna eventDate                                                                                               |
| **month**            | Puede extraerse de la columna eventDate                                                                                               |
| **year**             | Puede extraerse de la columna eventDate                                                                                               |
| **taxonKey**         | Identificador técnico de GBIF sobre la taxonomía, no relevante                                                                        |
| **speciesKey**       | Similar a taxonKey: identificador administrativo no requerido.                                                                        |
| **collectionCode**   | Metadato administrativo de la institución proveedora de los datos, no relevante                                                       |
| **catalogNumber**    | Identificador de colección de la institución proveedora; no aporta al análisis espacial.                                              |
| **identifiedBy**     | Nombre del identificador; irrelevante para el análisis ecológico.                                                                     |
| **license**          | Metadato legal que no afecta el análisis técnico.                                                                                     |
| **rightsHolder**     | Metadato legal-administrativo sin impacto en el estudio.                                                                              |
| **recordedBy**       | Nombre del colector; irrelevante para el análisis.                                                                                    |
| **lastInterpreted**  | Metadata de procesamiento; irrelevante para los análisis.                                                                             |
| **issue**            | Errores detectados por GBIF que ya fueron gestionados previamente.                                                                    |
**Tabla 3.** Columnas eliminadas manualmente y la justificación
## Resumen de limpieza de columnas
Importación de dataset
``` python
observaciones = pd.read_csv("Data/0016395-251025141854904.csv", sep="\t")
```
Ver las columnas originales
```python 
print(observaciones.columns.tolist())
num_columnas = observaciones.shape[1]
print(f"El número de columnas es: {num_columnas}")
```

```json
['gbifID', 'datasetKey', 'occurrenceID', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'infraspecificEpithet', 'taxonRank', 'scientificName', 'verbatimScientificName', 'verbatimScientificNameAuthorship', 'countryCode', 'locality', 'stateProvince', 'occurrenceStatus', 'individualCount', 'publishingOrgKey', 'decimalLatitude', 'decimalLongitude', 'coordinateUncertaintyInMeters', 'coordinatePrecision', 'elevation', 'elevationAccuracy', 'depth', 'depthAccuracy', 'eventDate', 'day', 'month', 'year', 'taxonKey', 'speciesKey', 'basisOfRecord', 'institutionCode', 'collectionCode', 'catalogNumber', 'recordNumber', 'identifiedBy', 'dateIdentified', 'license', 'rightsHolder', 'recordedBy', 'typeStatus', 'establishmentMeans', 'lastInterpreted', 'mediaType', 'issue']
El número de columnas es: 50
```
Eliminar columnas con porcentaje de nulos mayor o igual al 40%
```python
observaciones= observaciones.loc[:, observaciones.isnull().mean() < (40 / 100)]
```

```json
['gbifID', 'datasetKey', 'occurrenceID', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'taxonRank', 'scientificName', 'verbatimScientificName', 'countryCode', 'locality', 'stateProvince', 'occurrenceStatus', 'publishingOrgKey', 'decimalLatitude', 'decimalLongitude', 'eventDate', 'day', 'month', 'year', 'taxonKey', 'speciesKey', 'basisOfRecord', 'institutionCode', 'collectionCode', 'catalogNumber', 'identifiedBy', 'license', 'rightsHolder', 'recordedBy', 'lastInterpreted', 'issue']
El número de columnas es: 36
```
Eliminar columnas que no son relevantes para el estudio en base a la justificación previamente mostrada
```python
observaciones = observaciones.drop([
    'gbifID', 'datasetKey', 'occurrenceID',  'publishingOrgKey',
    'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 
    'taxonRank', 'scientificName', 'countryCode', 'occurrenceStatus', 
    'day', 'month', 'year', 'taxonKey','speciesKey', 
    'collectionCode', 'catalogNumber', 'identifiedBy', 'license', 
    'rightsHolder', 'recordedBy', 'lastInterpreted', 'issue'
], axis=1)
```

```json
['verbatimScientificName', 'locality', 'stateProvince', 'decimalLatitude', 'decimalLongitude', 'eventDate', 'basisOfRecord', 'institutionCode']
El número de columnas es: 8
```

# Limpieza de filas
Todavía no se han eliminado registros del dataset original, y este cuenta con $23,672$ registros de los cuales con el siguiente código se determina el comportamiento de los valores faltantes.
```python
import pandas as pd
total_registros = len(observaciones)
conteo_nulos = observaciones.isnull().sum()
porcentaje_nulos = (conteo_nulos / total_registros) * 100
resumen_nulos = pd.DataFrame({
    'Número de Nulos': conteo_nulos,
    'Porcentaje de Nulos': porcentaje_nulos.round(2)
})
resumen_nulos = resumen_nulos.sort_values(by='Porcentaje de Nulos', ascending=False)
print(resumen_nulos)
```

| Columna                | Número de Nulos | Porcentaje de Nulos |
| :--------------------- | :-------------: | :-----------------: |
| locality               |      5,201      |        21.97        |
| eventDate              |      5,088      |        21.49        |
| institutionCode        |      4,762      |        20.12        |
| decimalLatitude        |      4,135      |        17.47        |
| decimalLongitude       |      4,135      |        17.47        |
| stateProvince          |       446       |        1.88         |
| verbatimScientificName |       172       |        0.73         |
| basisOfRecord          |        0        |        0.00         |
**Tabla 4.** Porcentaje de valores faltantes por cada columna antes de limpiar las filas

En el hipotético caso de que los 5,201 registros vacíos de la columna `locality` contuvieran a los faltantes de las demás columnas, la limpieza de los registros sería tan sencilla como eliminar aquellos en donde `locality` sea un valor faltante, sin embargo, es rara la vez que se da esta coincidencia, así que partiendo de las columnas más importantes (por que contienen información de la que se puede inferir el valor de las demás) y que además tienen mayor porcentaje de nulos son **eventDate**, **decimalLatitude** y **decimalLongitude**. De manera que hay tres maneras de proceder con la limpieza ahora:
- Dejar solamente los registros que no tengan nulos en estas 3 columnas, esto garantiza un análisis espacio-temporal íntegro ya que la fecha y ubicación estarán completas, aunque también implica eliminar más registros.
- Eliminar solamente los registros que no contengan datos en `eventDate`, esta alternativa tiene la ventaja de que no se pierden tantos datos como en la primera opción y sería conveniente si se busca realizar solamente un análisis del tiempo.
- Eliminar solamente los registros que no contengan datos en la latitud y longitud, la ventaja, además de preservar más filas que en la primera ópción, con la desventaja de que solo permitiría un análisis espacial completo.
Ya que el objetivo del estudio es realizar un análisis exploratorio espacio-temporal, se procederá con la primera opción.
## Limpieza de valores faltantes en columnas espacio-temporales
Partimos con $23,672$ registros del dataset original
Ahora al eliminar los registros en cuyo campo `eventDate` el valor sea faltante, nos quedamos con $18,584$ registros.
```python
observaciones = observaciones.dropna(subset=['eventDate'])
```
Ya que los registros donde falta la latitud son los mismos donde falta la longitud, con eliminar los nulos de uno de estos es suficiente, ahora quedamos con $15,677$ registros.
```python
observaciones = observaciones.dropna(subset=['decimalLatitude'])
```
El reporte de los valores nulos de cada columna queda así

| Columna                | Número de Nulos | Porcentaje de Nulos |
| :--------------------- | :-------------: | :-----------------: |
| locality               |      5061       |        32.28        |
| institutionCode        |      2069       |        13.20        |
| stateProvince          |       143       |        0.91         |
| verbatimScientificName |       30        |        0.19         |
| decimalLatitude        |        0        |        0.00         |
| decimalLongitude       |        0        |        0.00         |
| eventDate              |        0        |        0.00         |
| basisOfRecord          |        0        |        0.00         |
**Tabla 5.** Porcentaje de valores faltantes por cada columna después de limpiar las filas espacio-temporales

Finalmente quedan las columnas de `locality`, y `stateprovince` cuyo valor se puede imputar con geocodificación inversa empleando librerías como `geopy` y `nominatim-api`, sin embargo no se realizará esto ya que, de acuerdo a la página https://geopy.readthedocs.io/en/stable/#geopy-is-not-a-service la primera librería sirve para implementar un frontend que haga llamadas a la api de la segunda librería, las cuales tienen restricciones en el número de llamadas por segundo.
Se van a limpiar los valores de la columna `stateProvince` ya que son pocos faltantes(143) y serán los que se usarán en los filtros que se usarán en el análisis de manera que es importante tener esta columna íntegra. Mientras tanto la columna `locality` se mantendrá como está, ya que a pesar de tener 5061 registros nulos, su función es más anecdótica en el sentido de que si el usuario quiere filtrar por estado, puede revisar si también existe una localidad registrada, pero esta columna no será clave en los procesos de filtrado. 
Al limpiar esta columna nos quedamos con $15,534$ registros
```python
observaciones = observaciones.dropna(subset=['stateProvince'])
```
## Limpieza de la columna de nombres científicos
Finalmente es necesario limpiar la columna `verbatimScientificName` que contiene solamente el nombre científico de la especie, esta columna, además de tener 30 valores nulos, tiene valores no nulos que no tienen el formato adecuado para el análisis, así que también se eliminarán.

| Columna                | Número de Nulos | Porcentaje de Nulos |
| :--------------------- | :-------------: | :-----------------: |
| locality               |      5045       |        32.48        |
| institutionCode        |      2067       |        13.31        |
| verbatimScientificName |       30        |        0.19         |
| stateProvince          |        0        |        0.00         |
| decimalLatitude        |        0        |        0.00         |
| decimalLongitude       |        0        |        0.00         |
| eventDate              |        0        |        0.00         |
| basisOfRecord          |        0        |        0.00         |
**Tabla 6.** Porcentaje de valores faltantes por cada columna 

Ahora el dataset tiene $15,504$ filas, gracias a que se eliminaron los valores faltantes de esta columna
```python
observaciones = observaciones.dropna(subset=['verbatimScientificName'])
```

Hay varios 163 registros que no están con el nombre científico, sino con el *Barcode of Life Data System* o *BOLD* que es un estándar que registra información genética de los seres vivos de acuerdo a https://pmc.ncbi.nlm.nih.gov/articles/PMC1890991/, ya que esta es una nomenclatura ajena a la que se está usando, se eliminarán las filas que la usen.
```python
valores_a_eliminar = ['BOLD:AAA4521', 'BOLD:AAB8771', 'BOLD:AAD2034', 
                      'BOLD:AAD2035', 'BOLD:ABX5622', 'BOLD:ACF4793']
observaciones = observaciones[~observaciones['verbatimScientificName'].isin(valores_a_eliminar)]
```
Ahora el dataframe consta de $15,341$ registros
Hay filas que están completamente en mayúsculas como "LEPUS CALIFORNICUS TEXIANUS", así que aquellos valores que están completamente en mayúsculas hay que editarlos para que solo la primera letra esté en mayúscula, lógicamente esta maniobra no cambia el número de registros
```python
es_todo_mayusculas = observaciones['verbatimScientificName'].str.isupper()
observaciones.loc[es_todo_mayusculas, 'verbatimScientificName'] = \
    observaciones.loc[es_todo_mayusculas, 'verbatimScientificName'].str.capitalize()
```
## Filtro geográfico, ortografía de los estados y formato de fecha
Hay múltiples registros que por coordenadas tienen valores erróneos, que por ejemplo son (0,0) o hacen referencia a locaciones en otros países o continentes, para eliminar estas filas se ejecuta
```python
observaciones = observaciones[
    (observaciones['decimalLatitude'] >= 14) & 
    (observaciones['decimalLatitude'] <= 33) &
    (observaciones['decimalLongitude'] >= -118) &
    (observaciones['decimalLongitude'] <= -86)
]
```
Y terminamos con $14,171$ registros
Son múltiples los estados que tienen errores ortográficos o bien es un nombre abreviado o demasiado largo (e.g. Veracruz de Ignacio de la Llave en vez de Veracruz. En vez de Michoacán), con la función `replace()`de `pandas` se pueden corregir, esta es una muestra de esta tarea con el estado de Michoacán.
```python
observaciones['stateProvince'] = observaciones['stateProvince'].replace(
    ['Michoacan','Michoacan de ocampo','Michoacán State','Michoac��n'],
    'Michoacán')
```
Esta misma lógica se aplica para el resto de los estados, como se observa en la tabla

| Nombre no estandarizado de estados                        | Corrección          |
| :-------------------------------------------------------- | :------------------ |
| Baja California Norte, Baja california, baja california   | Baja California     |
| Baja california sur                                       | Baja California Sur |
| Ciudad de mexico                                          | Ciudad de México    |
| Coahuila de zaragoza                                      | Coahuila            |
| Distrito federal, Distrito Federal                        | Ciudad de México    |
| Mexico, Mexico/Puebla                                     | México              |
| Michoacan, Michoacan de ocampo, Michoacán State, Michoacn | Michoacán           |
| Nuevo Leon, Nuevo leon, Nuevo Len                         | Nuevo León          |
| Queretaro                                                 | Querétaro           |
| Quintana roo                                              | Quintana Roo        |
| San Luis Potosi, San luis potosi                          | San Luis Potosí     |
| Veracruz State, Veracruz de ignacio de la llave           | Veracruz            |
| Yucatan                                                   | Yucatán             |
**Tabla 7.** Diccionario de correciones
Con este movimiento el dataset queda en $14,171$ registros
La columna `eventDate` tiene un formato estándar `yyyy-mm-dd` en la mayoría de los casos, con excepción de valores como `2014-06-01T13:40:26`, para corregir esto se hace un equivalente a un substring de los primeros 10 caracteres para homogeneizar la columna, además de asignarle el tipo `datetime` para realizar filtros de tiempo.
```python
observaciones['eventDate'] = observaciones['eventDate'].astype(str).str[:10]
observaciones['eventDate'] = pd.to_datetime(observaciones['eventDate'], errors='coerce')
```
Al final se pueden resetear los índices del dataframe para que en vez de tener valores salteados debido a las filas eliminadas, sea un índice continuo
```python
observaciones = observaciones.reset_index()
```
