# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 14:57:21 2023

@author: luisr
"""
#%%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random

#%%
provincia = pd.read_csv(r".\TablasLimpias\provincia.csv", index_col=0)
departamento = pd.read_csv(r".\TablasLimpias\departamento.csv", index_col=0)
establecimiento_productivo = pd.read_csv(r".\Tablaslimpias\establecimiento_productivo.csv",
                                         index_col=0)
operador_organico = pd.read_csv(r".\TablasLimpias\operador_organico.csv",
                                index_col=0)
rubro = pd.read_csv(r".\TablasLimpias\rubro.csv", index_col=0)
productos = pd.read_csv(r".\TablasLimpias\productos.csv", index_col=0)
operador_produce = pd.read_csv(r".\TablasLimpias\operador_produce.csv", index_col=0)

#%%

# =============================================================================
# Cantidad de establecimientos productivos por provincia
# =============================================================================



establecimientos_provincia = pd.merge(establecimiento_productivo[['ID_establecimiento','ID_departamento','proporcion_mujeres']],
                                      departamento[['ID_departamento','ID_provincia']],
                                      on = 'ID_departamento',
                                      how = 'left')

establecimientos_provincia = pd.merge(establecimientos_provincia,
                                      provincia,
                                      on = 'ID_provincia',
                                      how = 'left')

cant_provincia = establecimientos_provincia.Nombre.value_counts()

cant_provincia = cant_provincia.reset_index()

cant_provincia.columns = ['nombre','cantidad']

#%%
cmap = plt.get_cmap('tab20b')
colors = [cmap(i) for i in np.linspace(0,1,24)]
colors = colors[::3] + colors[2::3] + colors[1::3]

#%%

fig, ax1 = plt.subplots(1, 1, figsize=(24,12))
ax1.bar(cant_provincia.index, cant_provincia['cantidad'],
        label = list(cant_provincia['nombre']),
        color = colors)
plt.xticks(np.arange(cant_provincia.shape[0]),list(cant_provincia['nombre']),
           rotation='vertical')
plt.xlabel('Provincia/Entidad administrativa')
plt.ylabel('Establecimientos Productivos')
fig.suptitle('Cantidad de Establecimientos por provincia')  
plt.subplots_adjust(bottom=0.30)   
plt.savefig('bar.png',format = 'png')    

#%%

# =============================================================================
# Cantidad de productos por operador organico certificado por provincia
# =============================================================================

organicos_provincia = pd.merge(operador_organico[['ID_operador','ID_departamento']],
                                      departamento[['ID_departamento','ID_provincia']],
                                      on = 'ID_departamento',
                                      how = 'left')

organicos_provincia = pd.merge(organicos_provincia, provincia,
                                      on = 'ID_provincia',
                                      how = 'left')

organicos_provincia = pd.merge(organicos_provincia,
                               operador_produce,
                               on='ID_operador')

organicos_provincia = organicos_provincia.drop(columns = ['ID_departamento','ID_provincia'])

organicos_provincia = organicos_provincia.groupby(by=['Nombre','ID_operador']).count()

organicos_provincia = organicos_provincia.reset_index()

organicos_provincia.columns = ['provincia', 'operador', 'cant_productos']

prov = []
datos_boxplot = []

for p in organicos_provincia.provincia.unique():
    
    prov.append(p)
    filtro = organicos_provincia.provincia == p
    datos_boxplot.append(organicos_provincia['cant_productos'][filtro])

#%%
titulo_principal = "Cantidad de productos por operador"

fig, ax1 = plt.subplots(1, 1, figsize=(18,16))
ax1.boxplot(datos_boxplot, vert=False)
ax1.set_title(titulo_principal)
ax1.set(xlabel='Cantidad')
ax1.set_yticks(np.arange(1,len(prov)+1), prov)
plt.subplots_adjust(left=0.25)
plt.savefig('boxplot_cantidad.png', format='png')


#%%

# =============================================================================
# Relacion entre proporcion de mujeres y cantidad de operadores organicos 
# certificados
# =============================================================================

medias = []
cantidad_organicos = []

for p in prov:
    filtro_e = establecimientos_provincia.Nombre == p
    medias.append(np.mean(establecimientos_provincia['proporcion_mujeres'][filtro_e]))
    
    filtro_o = organicos_provincia.provincia == p 
    cantidad_organicos.append(len(organicos_provincia['operador'][filtro_o].unique()))
    
#%%

fig, ax1 = plt.subplots(1, 1, figsize=(24,12))

for i in range(len(prov)):
    ax1.scatter(cantidad_organicos[i], medias[i],
                label = prov[i], color = colors[i], marker = 'o')
    
for i, txt in enumerate(prov):
    ax1.annotate(txt, (cantidad_organicos[i], medias[i]), rotation=20)
    
plt.title('Relacion entre cantidad de operadores y proporcion de mujeres')
plt.xlabel('Cantidad de operadores orgánicos')
plt.ylabel('Proporcion de mujeres')  
plt.savefig('scatter.png',format = 'png') 


#%%

# =============================================================================
# Graficos de violin
# =============================================================================


establecimientos_provincia = pd.merge(establecimiento_productivo[['proporcion_mujeres','ID_departamento']],
                                      departamento[['ID_departamento','ID_provincia']],
                                      on = 'ID_departamento',
                                      how = 'left')

establecimientos_provincia = pd.merge(establecimientos_provincia,
                                      provincia,
                                      on = 'ID_provincia',
                                      how = 'left')

establecimientos_provincia = establecimientos_provincia.drop(columns=['ID_departamento','ID_provincia'])
establecimientos_provincia = establecimientos_provincia.iloc[:,[1,0]]
establecimientos_provincia.columns = ['provincia','proporcion_mujeres']

prov = []
datos_boxplot = []

for p in establecimientos_provincia.provincia.unique():
    
    prov.append(p)
    filtro = establecimientos_provincia.provincia == p
    datos_boxplot.append(establecimientos_provincia['proporcion_mujeres'][filtro])

#%%
plt.figure(figsize=(24,12))
grafico = sns.violinplot(x = 'provincia', y = 'proporcion_mujeres',
               data=establecimientos_provincia, orient='v',
               palette=colors)
plt.xticks(rotation = 'vertical')
plt.xlabel('Provincia/Entidad administrativa')
plt.ylabel('Proporcion')
fig.suptitle('Proporcion mujeres por provincia', )     
plt.subplots_adjust(bottom=0.30)   
plt.savefig('violin.png',format = 'png') 


#%%

# =============================================================================
# Cantidad de Establecimientos Productivos (CEP) vs. Cantidad de
# Establecimientos de Productores Orgánicos (CEO) de cada Provincia.
# =============================================================================

cantidad_provincia = [cant_provincia.cantidad[cant_provincia.nombre == p].iloc[0] for p in prov]

fig, ax1 = plt.subplots(1, 1, figsize=(16,18))

for i in range(len(prov)):
    ax1.scatter(cantidad_organicos[i], cantidad_provincia[i],
                label = prov[i], color = colors[i], marker = 'o')
    
rotaciones = [random.sample(['horizontal', 30], k = 1)[0] for _ in range(24)]
    
for i, txt in enumerate(prov):
    ax1.annotate(txt, (cantidad_organicos[i], cantidad_provincia[i]), rotation = rotaciones[i])
    
plt.title('Relacion entre cantidad de productores organicos y cantidad de establecimientos')
plt.xlabel('Cantidad de Operadores Orgánicos')
plt.ylabel('Cantidad de Establecimientos')  
plt.savefig('scatter2.png',format = 'png') 
plt.show()
