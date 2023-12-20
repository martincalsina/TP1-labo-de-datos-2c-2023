# %%
import numpy as np
import pandas as pd

# %%
import string
import re

# %%
! pip show inline_sql --version

# %%
import inline_sql

# %% [markdown]
# ## AFIP

# %%
ruta = ".\TablasOriginales\clae_agg.csv"
clae = pd.read_csv(ruta)

# %% [markdown]
# ### Documetación del dataset
# 
# |Título de la columna|Tipo de dato|Descripción|
# |:------------------:|------------|-----------|
# |clae6|Número entero (integer)|Nomenclador de mayor desagregación con el que AFIP caracteriza a los sectores de actividad|
# |clae6_desc|Texto (string)|Descripción de la actividad codificada a seis dígitos|
# |clae3|Número entero (integer)|Nomenclador a tres dígitos con el que AFIP caracteriza a los sectores de actividad|
# |clae3_desc|Texto (string)|Descripción de la actividad codificada a tres dígitos|
# |clae2|Número entero (integer)|Nomenclador a dos dígitos con el que AFIP caracteriza a los sectores de actividad|  
# |clae2_desc|Texto (string)|Descripción de la actividad codificada a dos dígitos|
# |letra|Texto (string)|Nomenclador de mayor agregación con el que AFIP caracteriza a los sectores de actividad|
# |letra_desc|Texto (string)|Descripción de la actividad codificada con letra|

# %%
clae.head()

# %%
clae.letra.unique()

# %%
clae.clae2.unique()

# %%
pd.unique(clae.clae6_desc)

# %%
def quitar_acentos(string):
    x = string
    x = x.replace('Á','A').replace('É','E').replace('Í','I')
    x = x.replace('Ó','O').replace('Ú','U')
    return x

def organizar_string(string):
    x = string.strip()
    x = x.upper()
    x = quitar_acentos(x)
    x = re.sub(r'\s+', ' ', x)
    return x

# %%
pd.unique(clae.clae3_desc)

# %%
clae.clae3_desc = clae.clae3_desc.apply(organizar_string)
pd.unique(clae.clae3_desc)

# %%
pd.unique(clae.clae2_desc)

# %%
pd.unique(clae.letra_desc)

# %%
clae.letra_desc = clae.letra_desc.apply(organizar_string)

# %%
pd.unique(clae.letra_desc)

# %%
clae[clae.clae2 == 99].shape

# %%
## Asumo que es un error que figure 999 como clae2 y corresponde a 99

# %%
clae['clae2'] = clae['clae2'].apply(lambda x: 99 if x == 999 else x)

# %% [markdown]
# ## INDEC

# %%
ruta = ".\TablasOriginales\localidad_bahra.csv"
indec = pd.read_csv(ruta, encoding='UTF-8')

# %%
indec.head()

# %%
indec.columns

# %%
indec = indec[['gid','nombre_geografico','nombre_departamento','codigo_indec_departamento','codigo_indec_provincia','nombre_provincia']]
indec.head()

# %%
indec.shape

# %%
columnas_sin_gid = indec.columns[indec.columns != 'gid']

# %%
### observo que hay dos localidades que le corresponden los mismos nombres, departamento y provincia
### asumo valores duplicados

indec.groupby(by=list(columnas_sin_gid)).count().sort_values(by='gid', ascending = False)

# %%
indec.drop_duplicates(subset=columnas_sin_gid, inplace=True)
indec.shape

# %%
indec.isna().sum()

# %%
indec.dtypes

# %%
indec.nombre_provincia.value_counts()

# %%
for columna in ['nombre_geografico','nombre_departamento','nombre_provincia']:
    indec[columna] = indec[columna].apply(organizar_string)

# %%
indec.groupby(by=list(columnas_sin_gid)).count().sort_values(by='gid', ascending = False)

# %%
indec.nombre_provincia = indec.nombre_provincia.apply(lambda x: 'CIUDAD AUTONOMA DE BUENOS AIRES' if x == 'CIUDAD DE BUENOS AIRES' else x)

# %%
indec.nombre_departamento[indec.nombre_provincia == 'CIUDAD AUTONOMA DE BUENOS AIRES']

# %%
indec.codigo_indec_departamento[indec.nombre_provincia == 'CIUDAD AUTONOMA DE BUENOS AIRES']

# %%
indec.codigo_indec_provincia[indec.nombre_provincia == 'CIUDAD AUTONOMA DE BUENOS AIRES']

# %%
indec.codigo_indec_departamento[indec.codigo_indec_departamento == 2]

# %%
indec.codigo_indec_departamento[3526] = '2'

# %%
indec.nombre_departamento[3526] = 'CIUDAD AUTONOMA DE BUENOS AIRES'

# %%
indec['codigo_indec_departamento'] = indec.codigo_indec_departamento.astype('int')

# %%
departamentos_indec = set()

for _, tupla_relacion in indec[['nombre_departamento',	'codigo_indec_departamento',	'codigo_indec_provincia',	'nombre_provincia']].iterrows():
    provincia, departamento = tupla_relacion['nombre_provincia'], tupla_relacion['nombre_departamento']
    departamentos_indec.add((provincia, departamento))

departamentos_indec = pd.DataFrame(departamentos_indec, columns = ['provincia', 'departamento'])
departamentos_indec = departamentos_indec.sort_values(by=['provincia', 'departamento']).reset_index(drop=True)
departamentos_indec.head()

# %% [markdown]
# ## Dataset Operadores orgánicos

# %%
ruta = ".\TablasOriginales\padron-de-operadores-organicos-certificados.csv"
org = pd.read_csv(ruta, encoding='ISO-8859-1')

# %%
org.head()

# %%
org.shape

# %%
org.columns

# %%
# Para poder decir que una tabla está en Primera Forma Normal, debe ésta satisfacer que
# todos los valores que tienen en sus columnas son atómicos. Mas basta ver "productos" en ésta para darnos
# cuenta que no es el caso, hay varios registros con múltiples valores separados por coma o algún otro
# signo en esta columna.
# Por lo tanto, no se encuentra en 1FN. Luego, tampoco en 2FN, 3FN o FNBC.
# No se encuentra en ninguna de las formas normales que conocemos.

# %%
org.info()

# Los ids son de tipo int, mientras que el resto de columnas tienen el tipo object (string),
# como uno podría esperar.

# %%
# Veo que solo 7 elementos de todo el Dataframe son nulos. 
# Se encuentran en las columnas rubro y productos. Los descartamos.

org.isna().sum()

# %%
org = org.dropna(axis='index')

# %%
# Pero viendo un poco el dataset a mano, se ve que hay "INDEFINIDO" o "NC" como valores para algunas
# celdas. Veamos con qué frecuencia aparecen aquellos en distintas columnas.

# %%
# Columna pais


org["pais"].value_counts()

# los 1935 campos son ARGENTINA, no tiene datos faltantes.
# Para nuestro trabajo, probablemente podriamos prescindir de esta columna y
# pais_id, pues no aportan mayor información. Por ahora las dejamos.


# %%
org = org.drop(columns='pais')

# %%
for columna in ['provincia', 'departamento']:
    org[columna] = org[columna].apply(organizar_string)

# %%
# Columna provincia


org["provincia"].value_counts()


# Están todas las provincia y CABA, los 24 posibles valores. No hay nulos ni problemas con signos de
# puntuación o semejante.


# %%
# Columna departamento

org["departamento"].value_counts()

# No se ve nada extraño de momento, veamos si hay algún problema con la puntuación, tildes...

# %%
valores_unicos_ordenados = sorted(org["departamento"].unique())
len(valores_unicos_ordenados)

# Hay 353 valores.

# %%
# Noté que había un elemento 'INDEFINIDO', quiero ver cuántas veces aparece.


indefinidos_depto = org["departamento"].value_counts().loc["INDEFINIDO"]
print("Hay " + str(indefinidos_depto) + " elementos con valor INDEFINIDO")


# %%
# Son solo 1 de 1395. Por más que la columna 'departamento' sea de interés para el objetivo del trabajo,
# considero que no es recuperable y por la poca cantidad descartamos las observaciones.


filtro = org["departamento"] != "INDEFINIDO"
org = org[filtro]

# %%
def problema_encoding(caracteres:str):

    LETRAS = string.ascii_letters + string.digits + ' '
    i = 0
    while i < len(caracteres) and caracteres[i] in LETRAS:
        i += 1

    return i == len(caracteres)

# %%
codificacion = org.departamento.apply(problema_encoding)
codificacion.value_counts()

# %%
## Los siguientes departamentos tienen problemas de signo de puntuacion. Probablemente no coindcidan
## con los nombres dados por indec

org.departamento[~codificacion].unique()

# %%
## verificamos que los departamentos de cada provincia coincidan con sus nombres indec
## encontramos aun mas problemas que los previstos

problemas = []

for _, tupla_relacion in org[['provincia','departamento']].drop_duplicates().iterrows():
    provincia = tupla_relacion['provincia']
    departamento = tupla_relacion['departamento']
    verificacion = departamentos_indec[(departamentos_indec.provincia == provincia) & (departamentos_indec.departamento == departamento)]
    if len(verificacion) == 0:
        print(f'El departamento {departamento} de la provincia de {provincia} no se registra en la base de indec. Verificar escritura')
        problemas.append((provincia, departamento))

f'{len(problemas)} problemas encontrados.'

# %%
### pareciera haber problemas, e.g.Sabemos que en realidad Carmen de Patagones es una localidad del departamento Patagones, y figura como departamento Carmen de Patagones

# %%
# Hacemos un dataset con los nombres con problemas

problemas = pd.DataFrame(problemas, columns=['nombre_provincia','nombre_geografico'])
problemas.head()

# %%
problemas.shape

# %%
### por el correspondiente en el dataset de indec.

nombres_correctos = pd.merge(problemas, indec[['nombre_provincia','nombre_geografico','nombre_departamento']], on = ['nombre_provincia','nombre_geografico'], how = 'left')
nombres_correctos.head()

# %%
# Observo que hay departamentos repetidos y sospecho que hay localidades homonimas en distintos departamentos en la base de indec
# esto puede confimarse facilmente

indec[indec.nombre_geografico == 'LOS CARDALES']

# %%
## elimino duplicados, no puedo inferir el correcto

nombres_correctos = nombres_correctos.drop_duplicates(subset=['nombre_provincia','nombre_geografico'], keep=False)
nombres_correctos.head()

# %%
## de los 203 departamentos con problemas, puedo solucionar 114 y quedarian pendientes 89

print(nombres_correctos.notnull().sum())

nombres_correctos.shape[0] - nombres_correctos.notnull().sum()

# %%
for indice, tupla_relacion in org[['provincia','departamento']].iterrows():
    provincia = tupla_relacion['provincia']
    departamento = tupla_relacion['departamento']
    
    verificacion = indec[(indec.nombre_provincia == provincia) & (indec.nombre_departamento == departamento)]
    datos_correctos = nombres_correctos['nombre_departamento'][(nombres_correctos.nombre_provincia == provincia) & (nombres_correctos.nombre_geografico == departamento)]
    hay_solucion = np.sum(datos_correctos.notnull()) > 0

    if len(verificacion) == 0 and hay_solucion:

        org.loc[indice, 'departamento'] = datos_correctos.iloc[0]

# %%
## verificamos que los departamentos de cada provincia coincidan con sus nombres indec
## encontramos aun mas problemas que los previstos

problemas = []

for _, tupla_relacion in org[['provincia','departamento']].drop_duplicates().iterrows():
    provincia = tupla_relacion['provincia']
    departamento = tupla_relacion['departamento']
    verificacion = departamentos_indec[(departamentos_indec.provincia == provincia) & (departamentos_indec.departamento == departamento)]
    if len(verificacion) == 0:
        print(f'El departamento {departamento} de la provincia de {provincia} no se registra en la base de indec. Verificar escritura')
        problemas.append((provincia, departamento))

f'{len(problemas)} problemas encontrados.'

# %%
### vimos que había 89 departamentos con problemas, observamos que esto equivale a 90 registros de tabla

# %%
## transformamos en Dataset

problemas = pd.DataFrame(problemas, columns=['nombre_provincia','nombre_geografico'])
problemas.head()

# %%
## Hay problema con CIUDAD DE BUENOS AIRES, segun puedo observar

indec[['nombre_provincia','codigo_indec_provincia']].drop_duplicates().loc[3526]['nombre_provincia']

# %%
### ciudad autonoma de buenos aires esta mal escrito

org['departamento'] = org['departamento'].apply(lambda x: 'CIUDAD AUTONOMA DE BUENOS AIRES' if x == 'CIUDAD AUTONOMA BUENOS AIRES' else x)
org['provincia'] = org['provincia'].apply(lambda x: 'CIUDAD AUTONOMA DE BUENOS AIRES' if x == 'CIUDAD AUTONOMA BUENOS AIRES' else x)

# %%
problemas = []

for _, tupla_relacion in org[['provincia','departamento']].drop_duplicates().iterrows():
    provincia = tupla_relacion['provincia']
    departamento = tupla_relacion['departamento']
    verificacion = departamentos_indec[(departamentos_indec.provincia == provincia) & (departamentos_indec.departamento == departamento)]
    if len(verificacion) == 0:
        print(f'El departamento {departamento} de la provincia de {provincia} no se registra en la base de indec. Verificar escritura')
        problemas.append((provincia, departamento))

f'{len(problemas)} problemas encontrados.'

# %%
## habiamos inferido problemas en 89 nombres de departamento veamos que corresponden a 128 registros
## los dropeamos

indices = []

for indice, tupla_relacion in org[['provincia','departamento']].iterrows():
    provincia = tupla_relacion['provincia']
    departamento = tupla_relacion['departamento']
    verificacion = departamentos_indec[(departamentos_indec.provincia == provincia) & (departamentos_indec.departamento == departamento)]
    if len(verificacion) == 0:
        print(f'El departamento {departamento} de la provincia de {provincia} no se registra en la base de indec. Verificar escritura')
        indices.append(indice)

f'{len(indices)} registros con los problemas anteriores.'

# %%
org.shape

# %%
## por cantidad y no disponer de datos para arreglar, dropeamos

org.drop(labels=indices, axis=0, inplace=True)

# %%
org.shape

# %%
problemas = []

for indice, tupla_relacion in org[['provincia','departamento']].iterrows():
    provincia = tupla_relacion['provincia']
    departamento = tupla_relacion['departamento']
    verificacion = departamentos_indec[(departamentos_indec.provincia == provincia) & (departamentos_indec.departamento == departamento)]
    if len(verificacion) == 0:
        print(f'El departamento {departamento} de la provincia de {provincia} no se registra en la base de indec. Verificar escritura')
        indices.append(indice)

f'{len(problemas)} problemas encontrados.'

# %%
# Columna localidad
org["localidad"].value_counts()


# Hay muchísimos valores 'INDEFINIDA' e 'INDEFINIDO'. 1344 de 1392, ¿Qué hacer con esto?
# Nosotros queremos ver si existe alguna relación entre la producción orgánica y la proporción de
# mujeres empleadas en cada uno de los establecimientos de los departamentos de las provincias y/o departamentos
# ¿Necesitamos saber la localidad? Dado nuestro objetivo, parece que no, por lo que podemos deshacernos
# de esta columna.

# %%
org.drop("localidad", axis=1, inplace=True)

# %%
## Columna rubro

org.rubro.unique()

# %%
# quisieramos transformar lo anterior en estándar clae2. Miramos en conjunto categoria_desc para distinguir el contexto del rubro
# y poder decidir una actividad

# %%
org.categoria_desc.unique()

# %%
# para cada nivel de categoria_desc nos fijamos el rubro del productor orgánico

# %%
org.rubro[org.categoria_desc == 'Productores'].unique()

# %%
### Tomamos la siguiente regla de decision para productores:

dicc_clae2_rubro = {'AGRICULTURA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'FRUTICULTURA/HORTICULTURA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'GANADERIA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'HORTICULTURA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'FRUTICULTURA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'AGRICULTURA/GANADERIA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'APICULTURA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'AGICULTURA/HORTICULTURA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'RECOLECCION SILVESTRE': 'Agricultura, ganadería, caza y servicios relacionados',
                          'AGICULTURA/FRUTICULTURA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'FRUTICULTURA/AGRICULTURA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'GANADERIA/FRUTICULTURA': 'Agricultura, ganadería, caza y servicios relacionados',
                          'ACUICULTURA': 'Pesca y acuicultura'
                          } 


# %%
## repetimos para Elaboradores

org.rubro[org.categoria_desc == 'Elaboradores'].unique()

# %%
### Tomamos la siguiente regla de decision para productores:

dicc_clae2_elaboradores = {
                            'PRODUCTOS PARA EL CUIDADO PERSONAL': 'Elaboración de productos de tabaco',
                            'PROCESAMIENTO APICOLA': 'Agricultura, ganadería, caza y servicios relacionados',
                            'PROCESAMIENTO FRUTALES Y HORTALIZAS': 'Elaboración de productos alimenticios',
                            'PROCESAMIENTO CEREALES Y OLEAGINOSAS': 'Elaboración de productos alimenticios',
                            'ACOPIO Y ACONDICIONAMIENTO DE GRANOS': 'Elaboración de productos alimenticios',
                            'ELABORACION Y EXTRACCION DE ACEITE': 'Elaboración de productos alimenticios',
                            'PROCESAMIENTO CULTIVOS INDUSTRIALES': 'Elaboración de productos alimenticios',
                            'EMPAQUE DE HORTALIZAS': 'Elaboración de productos alimenticios',
                            'INDUSTRIALIZACION DE YERBA MATE': 'Elaboración de productos alimenticios',
                            'FRACCIONAMIENTO DE MIEL': 'Elaboración de productos alimenticios',
                            'FRACCIONAMIENTO DE TE, YERBA MATE': 'Elaboración de productos alimenticios',
                            'OTROS': 'Otros sectores',
                            'EMPAQUE DE FRUTAS NO CITRICAS': 'Elaboración de productos alimenticios',
                            'INDUSTRIA LACTEA': 'Elaboración de productos alimenticios',
                            'ALIMENTACION ANIMAL': 'Elaboración de productos alimenticios',
                            'ACONDICIONAMIENTO Y EMPAQUE': 'Elaboración de productos alimenticios',
                            'PANIFICACION, GRANOS Y CEREALES, HARINAS, LEGUMBRES, YERBA MATE, AZUCAR, MIEL': 'Elaboración de productos alimenticios',
                            'PROCESAMIENTO DE TE Y MOLINO YERBA MATE': 'Elaboración de productos alimenticios',
                            'ELABORACION , FRACCIONAMIENTO Y DEPOSITO DE HIERBAS AROMATICAS Y MEDICINALES': 'Elaboración de productos alimenticios',
                            'PROCESAMIENTO DE CEREALES Y OLEAGINOSAS.': 'Elaboración de productos alimenticios',
                            'FRIGORIFICOS Y EMPAQUE PARA  FRUTAS': 'Elaboración de productos alimenticios',
                            'ELABORACION GRANOS': 'Elaboración de productos alimenticios',
                            'LIMPIEZA DE GRANOS': 'Elaboración de productos alimenticios',
                            'ELABORACION': 'Elaboración de productos alimenticios',
                            'ELABORACION, FRACCIONAMIENTO Y EMPAQUE': 'Elaboración de productos alimenticios',
                            'ACOPIO': 'Agricultura, ganadería, caza y servicios relacionados',
                            'ELABORACION ': 'Elaboración de productos alimenticios',
                            'BODEGA VITIVINICOLA': 'Elaboración de bebidas',
                            'EXTRACCION DE ACEITE': 'Elaboración de productos alimenticios',
                            'PROCESAMIENTO DE MANI': 'Elaboración de productos alimenticios',
                            'PROCESAMIENTO DE MANI Y SOJA': 'Elaboración de productos alimenticios',
                            'ELABORACION DE DULCES': 'Elaboración de productos alimenticios',
                            'PROCESAMIENTO TEXTIL': 'Elaboración de productos de cuero y calzado',
                            'SECADO, ACONDICIONAMIENTO, ELABORACION Y ACOPIO': 'Elaboración de productos alimenticios',
                            'PROCESAMIENTO PRODUCTOS ORGANICOS': 'Elaboración de productos alimenticios',
                            'EXTRACCION DE MIEL': 'Elaboración de productos alimenticios',
                            'FRACCIONAMIENTO Y EMPAQUE DE ARROZ': 'Elaboración de productos alimenticios',
                            'ELABORACION DE JUGOS CONCENTRADOS Y FABRICA DE ACEITES ESENCIALES': 'Elaboración de productos alimenticios',
                            'ELABORACION DE JUGOS CONCENTRADOS, ACEITE ESCENCIAL Y PULPA DE CITRICOS': 'Elaboración de productos alimenticios',
                            'ELABORACION DE JUGOS Y BODEGA VITIVINICOLA': 'Elaboración de bebidas',
                            'SECADERO DE FRUTAS': 'Elaboración de productos alimenticios',
                            'ELABORACION DE PASAS DE UVA': 'Elaboración de productos alimenticios',
                            'SECADO DE FRUTAS': 'Elaboración de productos alimenticios',
                            'INDUSTRIA VITIVINICOLA': 'Elaboración de bebidas',
                            'INDUSTRIALIZACION DE FRUTAS DESECADAS': 'Elaboración de productos alimenticios',
                            'ALMACENAMIENTO': 'Almacenamiento y actividades de apoyo al transporte',
                            'FRIGORIFICO PARA  MOSTO': 'Elaboración de bebidas',
                            'SECADO': 'Elaboración de productos alimenticios',
                            'FRACCIONAMIENTO DE VINO': 'Elaboración de bebidas',
                            'EXTRACCION DE ACEITE Y ELABORACION DE ACEITUNAS Y OTROS': 'Elaboración de productos alimenticios',
                            'PROCESADO Y ENVASADO DE HORTALIZAS': 'Elaboración de productos alimenticios',
                            'ELABORACION DE JUGO CONCENTRADO': 'Elaboración de productos alimenticios',
                            'ELABORACION; FRACCIONAMIENTO; EMPAQUE; ACOPIO': 'Elaboración de productos alimenticios',
                            'SECADERO , MOLINO Y FRACCIONAMIENTO DE TE, YERBA MATE': 'Elaboración de productos alimenticios',
                            'DEPOSITO DE YERBA': 'Almacenamiento y actividades de apoyo al transporte',
                            'MOLINO DE YERBA MATE': 'Elaboración de productos alimenticios',
                            'PROCESAMIENTO DE TE': 'Elaboración de productos alimenticios',
                            'EMPAQUE DE HORTALIZAS Y FRUTAS NO CITRICAS': 'Elaboración de productos alimenticios',
                            'FRIGORIFICOS PARA  FRUTAS': 'Elaboración de productos alimenticios',
                            'ELABORACION DE JUGO CONCENTRADO DE MANZANA Y PERA ': 'Elaboración de productos alimenticios',
                            'EMPAQUE Y FRIGORIFICO DE FRUTAS NO CITRICAS': 'Elaboración de productos alimenticios',
                            'ELABORACION DE ACEITE DE ROSA MOSQUETA': 'Elaboración de productos de cuero y calzado',
                            'EMPAQUE Y FRIGORIFICO FRUTAS NO CITRICAS': 'Elaboración de productos alimenticios',
                            'ELABORACION DE MANZANA Y PERA DEHIDRATADA': 'Elaboración de productos alimenticios',
                            'ALMACENAMIENTO Y FRIO PARA FRUTAS NO CITRICAS': 'Almacenamiento y actividades de apoyo al transporte',
                            'EMPAQUE FRUTAS NO CITRICAS': 'Elaboración de productos alimenticios',
                            'EMPAQUE PARA FRUTA NO CITRICA': 'Elaboración de productos alimenticios',
                            'EMPAQUE Y FRIO': 'Almacenamiento y actividades de apoyo al transporte',
                            'SECADO; PELADO; ENVASADO; ALMACENAMIENTO': 'Elaboración de productos alimenticios',
                            'BODEGA VITIVINICOLA. ELABORACION DE MOSTO CONCENTRADO DE UVAS ': 'Elaboración de bebidas',
                            'ELABORACION DE MOSTO CONCENTRADO DE UVA': 'Elaboración de bebidas',
                            'BODEGA VITIVINICOLA Y ELABORACION DE  VINAGRE, MERMELADAS, HUMUS DE LOMBRIZ': 'Elaboración de bebidas',
                            'FRACCIONAMIENTO': 'Elaboración de productos alimenticios',
                            'ELABORACION DE MOSTO CONCENTRADO': 'Elaboración de bebidas',
                            'SECADO - DESPALILLADO - EMBOLSADO': 'Elaboración de productos alimenticios',
                            'ELABORACION DE DULCES Y FRUTAS EN ALMIBAR': 'Elaboración de productos alimenticios',
                            'EXTRACCION Y FRACCIONAMIENTO DE MIEL': 'Elaboración de productos alimenticios',
                            'INDUSTRIA CARNICA': 'Elaboración de productos alimenticios',
                            'ELABORACION, FRACCIONAMIENTO, ALMACENAMIENTO, CONGELADO': 'Elaboración de productos alimenticios',
                            'INDUSTRIALIZACION DE LIMON': 'Elaboración de productos alimenticios',
                            'EMPAQUE DE PRODUCTOS DE LIMON': 'Elaboración de productos alimenticios',
                            'ELABORACION Y ENVASADO': 'Elaboración de productos alimenticios',
                            'ELABORACION DE  JUGOS CONCENTRADOS Y FABRICA DE ACEITES ESENCIALES': 'Elaboración de productos alimenticios',
}

# %%
# Repetimos para comercializadores

org.rubro[org.categoria_desc == 'Comercializadores'].unique()

# %%
org.categoria_desc.value_counts()

# %%
### En el caso de comercializadoras, como siempre es comercio y no elaboración o produccion, consideramos adecuado
### el clae2_desc 'Comercio al por mayor y al por menor y reparación de vehículos automotores y motos' dado
### que otros clae de comercio discriminan entre venta al por mayor y menor y esto no lo sabemos.

# %%
# Unimos los diccionarios anteriores y mapeamos considerandolos

dicc_clae2_rubro.update(dicc_clae2_elaboradores)

org['clae2_desc'] = org.rubro.map(dicc_clae2_rubro)
org['clae2_desc'].isna().sum()

# %%
# Llenamos los valores correspondientes a comercio

org['clae2_desc'] = org['clae2_desc'].fillna('Comercio al por mayor y al por menor y reparación de vehículos automotores y motos')
org['clae2_desc'].isna().sum()

# %%
org.shape

# %%
## a partir de clae2_desc recuperamos el clae2

org = pd.merge(org, clae[['clae2_desc', 'clae2']].drop_duplicates(), on= 'clae2_desc', how = 'left')
org.head()

# %%
## a partir de clae2 recuperamos la letra del clae

org = pd.merge(org, clae[['clae2','letra']].drop_duplicates(), on= 'clae2', how='left')
org.head()

# %%
len(org['razón social'].unique()) == len(org['Certificadora_id'].unique())

# %%
org = org.drop(columns=['pais_id','rubro','categoria_desc','certificadora_deno','clae2_desc'])
org.head()

# %%
org.shape

# %%
org = pd.merge(org, indec[['nombre_departamento','nombre_provincia','codigo_indec_departamento']].drop_duplicates(),
                left_on=['provincia','departamento'],
                  right_on=['nombre_provincia','nombre_departamento'], how='left').drop(columns=['nombre_provincia','nombre_departamento'])

# %%
### Columna productos

org["productos"] = org["productos"].str.strip()
org["productos"] = org["productos"].str.replace(r'\s+', ' ', regex=True)
valores_unicos_ordenados = sorted(org["productos"].unique())
valores_unicos_ordenados

# %%
# noto que algunos elementos tienen un punto al final, mientras que otros no. Me encargo de quitar todo
# signo de puntuacion

# Reemplazar '+' , '-' , '?' y ';' por comas en la columna productos
org['productos'] = org['productos'].str.replace(r'[+\-?;]', ',', regex=True)
# Reemplazar las ' y '
org['productos'] = org['productos'].str.replace(r' Y ', ',', regex=True)
# Reemplazar los caracteres con dos puntos y algo más por simplemente lo que viene antes
org['productos'] = org['productos'].str.replace(r'[^:]+:', lambda x: x.group(0)[:-1], regex=True)

# %%
# Todavía quedan algunas celdas con valores que tienen texto entre paréntesis.
# Viéndolo con el explorador de variables, parece que no hacen más que dar una descripción algo más
# detallada del producto del que habla: el tipo de harina, de dónde es la chia, a qué se refieren con
# "frutas al natural", etc.
# Parece que algunos se pueden reemplazar por lo que tienen dentro del paréntesis, como frutas al natural,
# y en otros, como la chicha o las harinas, podemos quitar lo que tienen los paréntesis, pues parecen
# ser no más que muy pequeños detalles.


org['productos'] = org['productos'].str.replace(r'CHIA (SALVIA HISPANICA L)', 'CHIA', regex=True)

reemplazar_frutas_al_natural = {'CONFITURAS,FRUTAS AL NATURAL (FRAMBUESAS, FRUTILLAS, CASSIS, SAUCO, CEREZAS, ROSA MOSQUETA, MORA, ARANDANOS,FRUTOS DEL BOSQUE)':
                                'CONFITURAS, FRAMBUESAS, FRUTILLAS, CASSIS, SAUCO, CEREZAS, ROSA MOSQUETA, MORA, ARANDANOS,FRUTOS DEL BOSQUE'}
org['productos'].replace(reemplazar_frutas_al_natural, inplace=True)

# %%
def quitar_entre_parentesis(texto):
    return re.sub(r'\([^)]*\)', '', texto)

# %%
# Aplicar la función a la columna 'nombre_de_columna'
org['productos'] = org['productos'].apply(quitar_entre_parentesis)

# %%
def obtener_valores(lista_productos):
    valores = lista_productos.split(",")
    valores = [v.strip() for v in valores]
    return set(valores)

def obtener_productos(prod):
    productos = prod["productos"].copy()
    conjunto_valores = set()

    for producto in productos:
        try:
            conjunto_valores.update(obtener_valores(producto))
        except:
            print(producto)

    conjunto_valores.discard("")#que no se me cuelen espacios en blanco

    return conjunto_valores

# %%
prod_orga = pd.DataFrame(sorted(list(obtener_productos(org))),
                                      columns = ["producto"])

# %%
ruta = r'.\repetidos.csv'

with open(ruta, 'r') as csv:
    data = csv.read()

dict_productos_unificado = {}

for line in data.split('\n'):
    values = line.split(';')
    
    # Tomar el primer valor como clave
    key = values[0]
    
    # Asignar la clave al resto de los valores en el diccionario
    for value in values:
        if value.strip() != '':
            dict_productos_unificado[value.strip()] = key.strip()

# Verificación de la salida
for key, values in dict_productos_unificado.items():
    print(f"{key}: {values}")

# %%
prod_orga.reset_index(inplace=True)
prod_orga.columns = ['id_producto','producto']
prod_orga

# %%
def crear_relaciones(df, df_productos):
    filas_relacion = []
    for indice_fila, fila in df.copy().iterrows():
        # cada fila es una Serie que tiene como indice el nombre de la columna y
        # como valor el respectivo para el indice_fila

        # obtengo los productos que tiene este establecimiento
        productos = fila["productos"]
        productos_de_fila = obtener_valores(productos)
        productos_de_fila.discard("")

        # obtengo los indices de estos productos en prod_productos
        indices_productos = [df_productos[df_productos["producto"] == p].index[0] for p in productos_de_fila]

        for indice_producto in indices_productos:
            filas_relacion.append((indice_fila, indice_producto))

    df_establecimiento_producto = pd.DataFrame(filas_relacion, columns=["id_operador", "id_producto"])

    return df_establecimiento_producto

# %%
df_establecimiento_producto = crear_relaciones(org, prod_orga)
print(df_establecimiento_producto.shape)
df_establecimiento_producto.head()

# %%
prod_orga['producto2'] = prod_orga.producto.map(dict_productos_unificado)
prod_orga

# %%
df_establecimiento_producto = df_establecimiento_producto.merge(prod_orga[['id_producto','producto2']], on='id_producto')
df_establecimiento_producto

# %%
prod_orga = prod_orga.drop_duplicates(subset='producto2')
prod_orga

# %%
df_establecimiento_producto.drop(columns='id_producto', inplace= True)
df_establecimiento_producto = df_establecimiento_producto.merge(prod_orga[['id_producto', 'producto2']], on='producto2')
df_establecimiento_producto

# %%
df_establecimiento_producto.drop(columns='producto2', inplace=True)
df_establecimiento_producto

# %%
prod_orga = prod_orga.drop(columns = 'producto2')
prod_orga

# %%
columnas = ['id_operador'] + list(org.columns) 
org.reset_index(inplace=True)
org.columns = columnas
org.drop(columns='productos', inplace=True)
org.head()

# %%
org.shape

# %% [markdown]
# ## Dataset establecimientos productivos

# %%
ruta = ".\TablasOriginales\distribucion_establecimientos_productivos_sexo.csv"
prod = pd.read_csv(ruta)

# %% [markdown]
# |Título de la columna|Tipo de dato|Descripción|
# |:------------------:|------------|-----------|
# |ID|Texto (string)|Indicador único por establecimiento|
# |departamento|Texto (string)|Departamento del establecimiento|
# |provincia|Texto (string)|Provincia del establecimiento|
# |lat|Número decimal (number)|Latitud redondeada del establecimiento|
# |lon|Número decimal (number)|Longitud redondeada del establecimiento|
# |provincia_id|Número entero (integer)|Código de la provincia|
# |in_departamentos|Número entero (integer)|Código del departamento|
# |empleo|Texto (string)|Cantidad agrupada de empleo del establecimiento|
# |clae6|Número entero (integer)|Actividad de la empresa a nivel de seis dígitos (CLAE6)|
# |clae2|Número entero (integer)|Actividad de la empresa a nivel de dos dígitos (CLAE2)|
# |letra|Texto (string)|Actividad de la empresa a nivel de letra (CLAE Letra)|
# |Tipo_coordenada|Texto (string)|Campo que indica si el proceso de georreferenciación obtuvo un resultado específico o si se obtuvo la coordenada por aproximación|
# |proporcion_mujeres|Número decimal (number)|Proporción de mujeres en el establecimiento productivo|

# %%
prod.head()

# %%
prod.in_departamentos.unique()

# %%
prod.clae2.unique()

# %%
prod.shape

# %%
prod.proporcion_mujeres.dtype

# %%
prod.proporcion_mujeres.describe()

# %%
prod.isna().sum()

# %%
prod.empleo.value_counts()

# %%
mapa = {'a. 1-9': '1-9', 'b. 10-49': '10-49',
        'c. 50-199': '50-199', 'd. 200-499': '200-499',
        'e. 500+': '500+'}

prod.empleo = prod.empleo.map(mapa)

# %%
prod.provincia.value_counts()

# %%
prod['provincia'] = prod['provincia'].apply(lambda x: x.upper() if x != 'CABA' else 'CIUDAD AUTONOMA DE BUENOS AIRES')
prod['provincia'].value_counts()

# %%
prod.departamento.value_counts()

# %%
prod['departamento'] = prod['departamento'].apply(organizar_string)
prod['departamento'].value_counts()

# %%
prod[['provincia','departamento','ID']].groupby(by=['provincia','departamento']).count()

# %%
def problema_encoding(caracteres:str):

    LETRAS = string.ascii_letters + string.digits + ' '
    i = 0
    while i < len(caracteres) and caracteres[i] in LETRAS:
        i += 1

    return i == len(caracteres)

# %%
codificacion = prod.departamento.apply(problema_encoding)
codificacion.value_counts()

# %%
pd.unique(prod.departamento[~codificacion])

# %%
## reemplazo el indice indec de caba

prod['in_departamentos'].replace([2021, 2014, 2007, 2028, 2105, 2070, 2049, 2035, 2042, 2084, 2098,
       2091, 2077, 2056, 2063], 2, inplace= True)

# %%
comprobacion = pd.merge(prod[['provincia','departamento','in_departamentos']].drop_duplicates(), indec[['codigo_indec_departamento', 'nombre_departamento']],
                         left_on='in_departamentos', right_on='codigo_indec_departamento', how='left')


comprobacion[comprobacion['departamento'] != comprobacion['nombre_departamento']]

# %%
### me doy cuenta que hay un problema con los departamentos de tierra del fuego en el dataset de productores pues su codigo indec
### no figura en el padron

indec[indec['nombre_provincia'] == 'TIERRA DEL FUEGO']

# %%
# solucionamos tierra del fuego

prod['in_departamentos'] = prod['in_departamentos'].replace({94008:94007, 94015:94014, 94011:94007})

# %%
comprobacion = pd.merge(prod[['provincia','departamento','in_departamentos']], indec[['codigo_indec_departamento', 'nombre_departamento']],
                         left_on='in_departamentos', right_on='codigo_indec_departamento', how='left')


comprobacion[comprobacion['departamento'] != comprobacion['nombre_departamento']].drop_duplicates()

# %%
prod.shape

# %%
prod['nombre_departamento'] = comprobacion['nombre_departamento']
prod.drop(columns='departamento', inplace=True)

# %%
prod.shape

# %%
prod.isna().sum()

# %%
prod = prod[['ID','provincia_id','in_departamentos','nombre_departamento','empleo','proporcion_mujeres','clae2']]

# %% [markdown]
# # Relaciones a partir del DER

# %% [markdown]
# 1. $ \textbf{PROVINCIA}(\texttt{ID\_provincia}, \texttt{Nombre}) $
# 
# 2. $ \textbf{DEPARTAMENTO}(\texttt{ID\_departamento}, \texttt{Nombre}) $
# 
# 3. $ \textbf{ESTABLECIMIENTO\_PRODUCTIVO}(\texttt{ID\_establecimiento}, \texttt{proporcion\_mujeres}) $
# 
# 4. $ \textbf{OPERADOR\_ORGANICO}(\texttt{ID\_operador}, \texttt{Razon\_social}) $
# 
# 6. $ \textbf{PRODUCTOS}(\texttt{ID\_producto}, \texttt{Nombre}) $
# 
# 7. $ \textbf{RUBRO}(\texttt{clae2}, \texttt{clae\_letra}, \texttt{descripcion}) $

# %% [markdown]
# 1. $ \textbf{PROVINCIA}(\texttt{ID\_provincia}, \texttt{Nombre}) $
# 
# 2. $ \textbf{DEPARTAMENTO}(\texttt{ID\_departamento}, \texttt{Nombre}, \texttt{ID\_provincia}) \rightarrow $ *Estrategia de la foreign key para relacion 1:N entre DEPARTAMENTO y PROVINCIA*
# 
# 3. $ \textbf{ESTABLECIMIENTO\_PRODUCTIVO}(\texttt{ID\_establecimiento}, \texttt{proporcion\_mujeres}, \texttt{ID\_departamento}) \rightarrow $ *Estrategia de la foreign key para relacion 1:N entre ESTABLECIMIENTO y DEPARTAMENTO*
# 
# 4. $ \textbf{OPERADOR\_ORGANICO}(\texttt{ID\_operador}, \texttt{Razon\_social}, \texttt{ID\_departamento}) \rightarrow $ *Estrategia de la foreign key para relacion 1:N entre OPERADOR y DEPARTAMENTO*
# 
# 5. $ \textbf{PRODUCTOS}(\texttt{ID\_producto}, \texttt{Nombre}) $
# 
# 6. $ \textbf{RUBRO}(\texttt{clae2}, \texttt{clae\_letra}, \texttt{descripcion}) $
# 
# 7. $ \textbf{OPERADOR\_PRODUCE}(\texttt{ID\_operador}, \texttt{ID\_producto}) \rightarrow $  *Relacion muchos a muchos N:M entre RUBRO Y OPERADOR*

# %%
provincia = pd.DataFrame(columns=['ID_provincia','Nombre'])
provincia

# %%
departamento = pd.DataFrame(columns=['ID_departamento', 'Nombre', 'ID_provincia'])
departamento

# %%
establecimiento_productivo = pd.DataFrame(columns=['ID_establecimiento', 'proporcion_mujeres','ID_departamento','clae2'])
establecimiento_productivo

# %%
operador_organico = pd.DataFrame(columns=['ID_operador','Razon_social','ID_departamento','clae2'])
operador_organico

# %%
productos = pd.DataFrame(columns=['ID_producto', 'Nombre'])
productos

# %%
rubro = pd.DataFrame(columns=['clae2','letra','descripcion'])
rubro

# %%
operador_produce = pd.DataFrame(columns=['ID_operador','ID_producto'])
operador_produce

# %% [markdown]
# # Llenamos las tablas

# %%
sub_indec_provincia = indec[['codigo_indec_provincia','nombre_provincia']].drop_duplicates().sort_values(by='nombre_provincia').reset_index(drop=True)
sub_indec_provincia.columns = provincia.columns

provincia = pd.concat([provincia,sub_indec_provincia], axis=0)
provincia.head()

# %%
provincia.to_csv('.\TablasLimpias\provincia.csv')

# %%
sub_indec_departamento = indec[['codigo_indec_departamento','nombre_departamento','codigo_indec_provincia']].drop_duplicates().sort_values(by='nombre_departamento').reset_index(drop=True)
sub_indec_departamento.columns = departamento.columns

departamento = pd.concat([departamento,sub_indec_departamento], axis=0)
departamento.head()

# %%
departamento.to_csv('.\TablasLimpias\departamento.csv')

# %%
productivos = prod[['ID','proporcion_mujeres','in_departamentos','clae2']].drop_duplicates().reset_index(drop=True)
productivos.columns = establecimiento_productivo.columns

establecimiento_productivo = pd.concat([establecimiento_productivo,productivos], axis=0)
establecimiento_productivo.head()

# %%
productivos.shape

# %%
establecimiento_productivo.to_csv('.\TablasLimpias\establecimiento_productivo.csv')

# %%
organicos = org[['id_operador','razón social','codigo_indec_departamento','clae2']]
organicos.columns = operador_organico.columns

operador_organico = pd.concat([operador_organico,organicos], axis=0)
operador_organico.head()

# %%
operador_organico.to_csv('.\TablasLimpias\operador_organico.csv')

# %%
prod_orga.columns = productos.columns
productos = pd.concat([productos, prod_orga], axis=0)
productos.head()

# %%
productos.to_csv('.\TablasLimpias\productos.csv')

# %%
clae2_letra = clae[['clae2','letra','clae2_desc']].drop_duplicates()
clae2_letra.columns = rubro.columns
rubro = pd.concat([rubro, clae2_letra], axis=0)
rubro.head()

# %%
rubro.to_csv(r'.\TablasLimpias\rubro.csv')

# %%
df_establecimiento_producto.columns = operador_produce.columns
operador_produce = pd.concat([operador_produce, df_establecimiento_producto], axis=0)
operador_produce.head()

# %%
operador_produce.to_csv('.\TablasLimpias\operador_produce.csv')


