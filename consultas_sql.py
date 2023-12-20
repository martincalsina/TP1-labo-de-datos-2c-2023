# %% [markdown]
# Librerías

# %%
import pandas as pd
from inline_sql import sql

# %% [markdown]
# Dataframes

# %%
path = "./TablasLimpias/"

provincia = pd.read_csv(path+"provincia.csv", index_col=0)
departamento = pd.read_csv(path+"departamento.csv", index_col=0)
establecimiento_productivo = pd.read_csv(path+"establecimiento_productivo.csv", index_col=0)
operador_organico = pd.read_csv(path+"operador_organico.csv", index_col=0)
productos = pd.read_csv(path+"productos.csv", index_col=0)
operador_produce = pd.read_csv(path+"operador_produce.csv", index_col=0)
rubro = pd.read_csv(path+"rubro.csv", index_col=0)

# %%
establecimiento_productivo.shape

# %% [markdown]
# #Ejercicios

# %%
#FUNCION PARA PASAR A LATEX LAS TABLES

def pasar_latex(tabla):
  tabla_latex = tabla.to_latex(index=False)
  print(tabla_latex)

# %% [markdown]
# ### **i)** Para cada producto (producido por un productor orgánico) detallar en qué provincias se produce. El orden del reporte debe respetar la cantidad de provincias en las cuales se produce dicho producto (de mayor a menor). En caso de empate, ordenar alfabéticamente por nombre de producto.

# %%
#hacemos una query para relacionar cada producto con su nombre y el id de su operador
query_aux = """
             SELECT r.ID_operador, p.Nombre AS Producto
             FROM operador_produce AS r
             INNER JOIN productos AS p
             ON r.ID_producto = p.ID_producto
            """

producto_operador = sql^ query_aux

#ahora lo conectamos con el departamento del operador
query_aux_2 = """
                SELECT op.ID_departamento AS id_departamento, p.ID_operador, p.Producto
                FROM producto_operador AS p
                INNER JOIN operador_organico AS op
                ON p.ID_operador = op.ID_operador
              """

producto_operador_depto = sql^ query_aux_2

#ahora lo relacionamos con el id de la provincia
query_aux_3 = """
               SELECT DISTINCT d.ID_provincia,
               op.Producto
               FROM producto_operador_depto AS op
               INNER JOIN departamento AS d
               ON op.ID_departamento = d.ID_departamento
              """

producto_operador_depto_provincia = sql^ query_aux_3

#ya tenemos filas con el operador, los productos y la provincia donde se producen.
#necesitamos saber la cantidad de provincias en que se produce cada producto

query_provincias_por_producto = """
                                 SELECT Producto, COUNT(ID_provincia) AS cant_provincias
                                 FROM producto_operador_depto_provincia
                                 GROUP BY Producto
                                """

#el DISTINCT en la subquery principal es porque no queremos que se cuente dos veces,
#por ejemplo: "CAÑA DE AZUCAR, MISIONES" porque lo producen dos operadores, lo que nos importa
#es la cantidad de provincias en donde lo producen

temp_cant_provincias_por_producto = sql^query_provincias_por_producto

#tenemos la cantidad de provincias en las que se produce cada producto, pasamos a
#enlazar la query anterior a ésta con el resultado de ejecutar la de arriba

query_aux_4 = """
                SELECT p.Nombre AS Provincia,
                r.Producto
                FROM producto_operador_depto_provincia AS r
                INNER JOIN provincia AS p
                ON p.ID_provincia = r.ID_provincia
              """

temp_productos_y_provincias_donde_estan = sql^query_aux_4

#ya podemos conectar todo

query = """
          SELECT DISTINCT p.Producto, p.Provincia
          FROM temp_productos_y_provincias_donde_estan AS p
          INNER JOIN temp_cant_provincias_por_producto AS c
          ON p.Producto = c.Producto
          ORDER BY c.cant_provincias DESC, p.Producto
        """

provincias_productos_producidos = sql^query

# %%
provincias_productos_producidos.head()

# %% [markdown]
# ### **ii)** ¿Cuál es el CLAE2 más frecuente en establecimientos productivos? Mencionar el Código y la Descripción de dicho CLAE2

# %%
#hacemos una query que nos diga la frecuencia de los claes

query_aux = """
            SELECT clae2, COUNT(ID_ESTABLECIMIENTO) AS Frecuencia
            FROM establecimiento_productivo
            GROUP BY clae2
            ORDER BY Frecuencia DESC LIMIT 1
          """

clae_mas_frecuente = sql^ query_aux

#devuelve una tabla con cada clae2 y la cantidad de establecimientos productivos que lo tienen.
#Al estar ordenada  según frecuencia (100, 70, 20, 10, 5...), el LIMIT 1 devuelve la fila (clae2, Frecuencia) donde Frecuencia es máxima.

query = """
          SELECT r.clae2 AS Código, r.descripcion AS Descripción
          FROM rubro AS r
          WHERE r.clae2 = (
            SELECT clae_mas_frecuente.clae2
            FROM clae_mas_frecuente
          )
        """

clae2_mas_frecuente = sql^query

# %%
clae2_mas_frecuente.head()

# %% [markdown]
# ### **iii)** ¿Cuál es el producto más producido (que lo producen más establecimientos de operadores orgánicos)?¿Qué Provincia-Departamento los producen?

# %%
#PRIMERA PARTE DE LA PREGUNTA
#buscamos cuál es el producto más producido, es similar a lo que hicimos con el clae2

query_aux = """
              SELECT r.ID_producto AS id_producto, COUNT(r.ID_operador) AS Frecuencia
              FROM operador_produce AS r
              GROUP BY r.ID_producto
              ORDER BY Frecuencia DESC
              LIMIT 1
            """

producto_mas_producido = sql^ query_aux

#Obtenemos el id del producto que más operadores orgánicos lo tienen junto con su frecuencia

#obtenemos su nombre
query = """
                SELECT p.ID_producto AS id_producto, p.Nombre AS nombre_producto
                FROM producto_mas_producido AS p_mas_producido
                INNER JOIN productos AS p
                ON p_mas_producido.id_producto = p.ID_producto
              """

producto_mas_frecuente_organicos = sql^query

# %%
producto_mas_frecuente_organicos.head()

# %%
#SEGUNDA PARTE DE LA PREGUNTA
#obtenemos los id de departamentos de los operadores que lo producen, usamos el resultado anterior
query_aux = """
                SELECT DISTINCT op.ID_departamento AS id_departamento
                FROM operador_organico AS op
                INNER JOIN operador_produce AS r
                ON op.ID_operador = r.ID_operador
                WHERE r.ID_producto = 69
              """

#el DISTINCT es porque no nos interesa si hay más de un operador en un depto que lo produce, basta que haya uno

deptos_productores = sql^ query_aux

#ahora queremos saber también los nombres de esos deptos y sus provincias (id)
query_aux_2 = """
               SELECT d.ID_provincia AS id_provincia, d.ID_departamento AS id_departamento, d.Nombre AS Nombre
               FROM departamento AS d
               WHERE d.ID_departamento IN (
                SELECT deptos.id_departamento
                FROM deptos_productores AS deptos
               )
              """

provincias_deptos_productores = sql^ query_aux_2

#ahora podemos acceder a las provincias

query = """
           SELECT p.Nombre AS Provincia, d.Nombre AS Departamento
           FROM provincias_deptos_productores AS d
           INNER JOIN provincia AS p
           ON d.id_provincia = p.ID_provincia
           ORDER BY Provincia DESC, Departamento DESC
        """

lugares_produccion_organico_mas_frecuente = sql^query

# %%
lugares_produccion_organico_mas_frecuente.head()

# %% [markdown]
# ### **iv)** ¿Existen departamentos que no presentan Operadores Orgánicos Certificados? ¿En caso de que sí, cuántos y cuáles son?

# %%
#PRIMERA PARTE DE LA PREGUNTA

#primero queremos saber todos los deptos con operadores orgánicos
query_aux = """
              SELECT DISTINCT ID_departamento
              FROM operador_organico
            """

#Ahora que los sabemos, podemos hacer restarselos (como conjuntos) a todos los deptos que tenemos
query_aux_2 = """
         SELECT d.ID_departamento AS id_departamento
         FROM departamento AS d

         EXCEPT

         SELECT DISTINCT op.ID_departamento AS id_departamento
         FROM operador_organico AS op
        """

deptos_sin_organicos = sql^ query_aux_2

#esto nos da todos los ids de aquellos departamentos donde no hay operadores orgánicos,
#podemos ver cuántos son

query = """
          SELECT COUNT(d.id_departamento) AS Cantidad_Deptos_Sin_Organicos
          FROM deptos_sin_organicos AS d
        """

cant_deptos_sin_organicos = sql^query

# %%
cant_deptos_sin_organicos.head()

# %%
#SEGUNDA PARTE DE LA PREGUNTA

#vimos que sí existen deptos sin orgánicos, pero ya sabemos cuáles son sus id
#podemos recuperar sus nombres

query = """
          SELECT d.Nombre
          FROM departamento AS d
          WHERE d.ID_departamento IN (
              SELECT deptos_sin_organicos.id_departamento
              FROM deptos_sin_organicos
          )
        """

deptos_sin_organicos = sql^query

# %%
deptos_sin_organicos.head()

# %% [markdown]
# ### **v)** ¿Cuál es la tasa promedio de participación de mujeres en cada provincia?¿Cuál es su desvío? En cada caso, mencionar si es mayor o menor al promedio de todo el país

# %%
#PRIMERA y SEGUNDA PARTE DE LA PREGUNTA

#asociamos a cada establecimiento con su provincia
query_aux = """
              SELECT d.ID_provincia AS id_provincia, e.proporcion_mujeres
              FROM establecimiento_productivo AS e
              INNER JOIN departamento AS d
              ON e.ID_departamento = d.ID_departamento
            """

establecimiento_provincia_temp = sql^query_aux

#ahora lo asociamos con el nombre de la provincia
query_aux_2 = """
               SELECT p.ID_provincia AS id_provincia, p.Nombre AS Provincia, est_prov.proporcion_mujeres
               FROM establecimiento_provincia_temp AS est_prov
               INNER JOIN provincia AS p
               ON p.ID_provincia = est_prov.id_provincia
              """

#ahora podemos obtener los promedios por provincia

establecimiento_provincia = sql^ query_aux_2

query = """
          SELECT p.Provincia,
          MEAN(p.proporcion_mujeres) AS Promedio,
          STDDEV(p.proporcion_mujeres) AS Desvío_Estándar
          FROM establecimiento_provincia AS p
          GROUP BY p.Provincia
        """

promedios_desvios_por_provincia = sql^query

# %%
promedios_desvios_por_provincia.head(24)

# %%
#TERCERA PARTE DE LA PREGUNTA

#hay que obtener los valores para el promedio y desvío a nivel nacional

query_aux = """
              SELECT MEAN(e.proporcion_mujeres) AS Promedio_Nacional,
              STDDEV(e.proporcion_mujeres) AS Desvío_Estándar_Nacional
              FROM establecimiento_productivo AS e
            """

temp_datos_nivel_nacional = sql^query_aux
temp_datos_nivel_nacional.head()

# %%
#ya podemos decidir cuándo es mayor o menor a los datos nacionales

query = """
          SELECT p.Provincia,
          MEAN(p.proporcion_mujeres) AS Promedio,
          STDDEV(p.proporcion_mujeres) AS Desvío_Estándar,
          CASE WHEN Promedio >= (SELECT MEAN(e.proporcion_mujeres) FROM establecimiento_productivo AS e) THEN 'Mayor' ELSE 'Menor' END AS Respecto_Promedio_Nacional,
          CASE WHEN Desvío_Estándar > (SELECT STDDEV(e.proporcion_mujeres) FROM establecimiento_productivo AS e) THEN 'Mayor' ELSE 'Menor' END AS Respecto_Desvío_Nacional
          FROM establecimiento_provincia AS p
          GROUP BY p.Provincia
          ORDER BY p.provincia
        """

promedios_desvios_por_provincia_comparados = sql^query

# %%
promedios_desvios_por_provincia_comparados.head(24)

# %% [markdown]
# ### **vi)** Mostrar por cada provincia-departamento cuántos establecimientos productivos y cuántos emprendimientos orgánicos posee

# %%
#Obtenemos la cantidad de establecimientos productivos por departamento

query_aux = """
              SELECT e.ID_departamento AS id_departamento, COUNT(e.ID_establecimiento) AS establecimientos
              FROM establecimiento_productivo AS e
              GROUP BY e.ID_departamento
              ORDER BY establecimientos DESC
            """

cant_est_por_depto_temp = sql^ query_aux

#A los deptos sin establecimientos debemos ponerlos en cero

query_aux_2 = """
               SELECT d.ID_provincia AS id_provincia,
               d.ID_departamento AS id_departamento,
               d.Nombre AS Nombre,
               CASE WHEN d2.establecimientos IS NULL THEN 0 else d2.establecimientos END AS establecimientos
               FROM departamento AS d
               LEFT OUTER JOIN cant_est_por_depto_temp AS d2
               ON d.ID_departamento = d2.id_departamento
              """

cant_est_por_depto = sql^ query_aux_2
#hacemos exactamento lo mismo pero con operadores organicos

#obtenemos los organicos por departamento
query_aux_3 = """
              SELECT op.ID_departamento AS id_departamento, COUNT(op.ID_operador) AS operadores_organicos
              FROM operador_organico AS op
              GROUP BY op.ID_departamento
              ORDER BY operadores_organicos DESC
            """

cant_org_por_depto_temp = sql^ query_aux_3

#hacemos el left outer join con los deptos como antes

query_aux_4 = """
               SELECT d.ID_provincia AS id_provincia,
               d.ID_departamento AS id_departamento,
               d.Nombre AS Nombre,
               CASE WHEN d2.operadores_organicos IS NULL THEN 0 else d2.operadores_organicos END AS operadores_organicos
               FROM departamento AS d
               LEFT OUTER JOIN cant_org_por_depto_temp AS d2
               ON d.ID_departamento = d2.id_departamento
              """


cant_org_por_depto = sql^ query_aux_4
#ya está, ahora podemos hacer un inner join y juntar las dos tablas

query_aux_5 = """
          SELECT
          d1.id_provincia,
          d1.Nombre AS Departamento,
          d1.establecimientos AS Establecimientos_Productivos,
          d2.operadores_organicos As Operadores_Organicos
          FROM cant_est_por_depto AS d1
          INNER JOIN cant_org_por_depto AS d2
          ON d1.id_departamento = d2.id_departamento
        """

cant_productores_por_depto = sql^ query_aux_5

#Sólo queda relacionar cada depto con su provincia

query = """
          SELECT p.Nombre AS Provincia,
          d.Departamento,
          d.Establecimientos_Productivos,
          d.Operadores_Organicos
          FROM cant_productores_por_depto AS d
          INNER JOIN provincia AS p
          ON p.ID_provincia = d.id_provincia
          ORDER BY p.Nombre, d.Establecimientos_Productivos DESC, d.Departamento
        """

distribucion_establecimientos_y_organicos_por_departamento = sql^query

# %%
distribucion_establecimientos_y_organicos_por_departamento.head()

# %% [markdown]
# **RECU)** Listar la totalidad de las Provincias y sus Departamentos respetando el
# siguiente orden:
# 1. Las provincias con más departamentos al principio
# 2. En caso de empate, por orden alfabético de Nombre de Provincia
# 3. y dentro de provincia, por orden alfabético de nombre de
# Departamento

# %%
#obtenemos la cantidad de departamentos por provincia

query_aux = """
             SELECT p.id_provincia, COUNT(d.id_departamento) AS cantidad_departamentos
             FROM departamento AS d
             INNER JOIN provincia AS p
             ON d.id_provincia = p.id_provincia
             GROUP BY p.id_provincia
             ORDER BY cantidad_departamentos DESC
            """

cantidad_deptos = sql^ query_aux

#relacionamos a cada provincia con su cantidad de deptos

query_aux_2 = """
               SELECT p.id_provincia, p.Nombre AS Provincia, c.cantidad_departamentos
               FROM provincia AS p
               INNER JOIN cantidad_deptos AS c
               ON c.id_provincia = p.id_provincia
              """

provincias_con_cant_deptos = sql^ query_aux_2

#relacionamos a este nuevo dataframe con los deptos y vemos los resultados

query = """
          SELECT p.Provincia, d.Nombre AS Departamento
          FROM departamento AS d
          INNER JOIN provincias_con_cant_deptos AS p
          ON d.id_provincia = p.id_provincia
          ORDER BY p.cantidad_departamentos DESC, p.Provincia ASC, d.Nombre ASC
        """

provincias_con_mas_deptos = sql^ query

# %%
provincias_con_mas_deptos


