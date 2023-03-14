# Importar módulos necesarios (math para la cuadrícula y processing para "Count points in polygon")
import math
import processing

# Definir la capa de puntos 
arbres = QgsProject.instance().mapLayersByName('arbres')[0] 	### Nombre de nuestra capa de puntos entre comillas

# Obtener la extensión de la capa de puntos
xmin, ymin, xmax, ymax = arbres.extent().toRectF().getCoords()

# Definir la anchura y altura de los cuadros (50mx50m en este caso)
ancho = 50
alto = 50

# Definir el número de filas y columnas necesarias para cubrir la extensión
num_columnas = math.ceil((xmax - xmin) / ancho)
num_filas = math.ceil((ymax - ymin) / alto)

# Crear una capa shapefile vacía para los polígonos de cuadrícula
crs = arbres.crs()
recuadro = QgsVectorLayer('Polygon?crs=' + crs.authid(), 'recuadro', 'memory')
prov = recuadro.dataProvider()
prov.addAttributes([QgsField('id', QVariant.Int)])

# Crear una lista vacía para los polígonos de cuadrícula
poligonos = []

# Iterar sobre las filas y columnas para crear los polígonos de cuadrícula
for i in range(num_filas):
    for j in range(num_columnas):
        x1 = xmin + j * ancho
        y1 = ymin + i * alto
        x2 = x1 + ancho
        y2 = y1 + alto
        geom = QgsGeometry.fromRect(QgsRectangle(x1, y1, x2, y2))
        poligonos.append(geom)

# Agregar los polígonos a la capa de polígonos de cuadrícula
ids = []
for i, geom in enumerate(poligonos):
    f = QgsFeature()
    f.setGeometry(geom)
    f.setAttributes([i])
    success, id_ = prov.addFeatures([f])
    if success:
        ids.append(id_)

# Actualizar la extensión de la capa de polígonos de cuadrícula
recuadro.updateExtents()
recuadro.updateFields() ###Esta línea es necesaria para que nos salgan los atributos en la tabla de atributos. Si no no dejaría hacer el count points in polygon

# Agregar la capa de polígonos de cuadrícula al proyecto
QgsProject.instance().addMapLayer(recuadro)






# Definir los parámetros del algoritmo para el geoproceso
parametros = {
    "POLYGONS": "recuadro",   			### Nombre de nuestra capa de polígonos
    "POINTS": "arbres",       			### Nombre de nuestra capa de puntos
    "OUTPUT": "memory:capa_salida"   	### Nombre de la capa de salida (se guarda en memoria)
}

# Ejecutar el algoritmo Count Points in Polygon
resultado = processing.run("native:countpointsinpolygon", parametros)


# Acceder a la capa de salida (OUTPUT) y añadirla en el mapa en una capa de memoria
capa_salida = resultado["OUTPUT"]
QgsProject.instance().addMapLayer(capa_salida)
