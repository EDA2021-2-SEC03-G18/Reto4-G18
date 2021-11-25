"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
assert cf
import config
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
assert config

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""


# -----------------------------------------------------
#                       API
# -----------------------------------------------------


def newAnalyzer():
    try:
        analyzer = {
                    'airports': None,
                    'connections': None,
                    'airports_directed': None
                    }

        analyzer['airports'] = m.newMap(numelements=93000,
                                     maptype='PROBING',
                                     comparefunction=compareAirportsIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=93000,
                                              comparefunction=compareAirportsIds)

        analyzer['airports_directed'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=False,
                                              size=93000,
                                              comparefunction=compareAirportsIds)

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')




# ==============================
# Funciones de consulta
# ==============================

def addStopConnection(analyzer, lastservice, service):
    try:
        origin = formatVertex(lastservice)
        destination = formatVertex(service)
        cleanServiceDistance(lastservice, service)
        distance = float(service['distance_km']) - float(lastservice['distance_km'])
        distance = abs(distance)
        addStop(analyzer, origin)
        addStop(analyzer, destination)
        addConnection(analyzer, origin, destination, distance)
        addRouteStop(analyzer, service)
        addRouteStop(analyzer, lastservice)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addStopConnection')


def totalAirports(analyzer):
    """
    Retorna el total de vertices del grafo
    """
    return gr.numVertices(analyzer['connections'])


def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['connections'])



# ==============================
# Funciones Helper
# ==============================

def cleanServiceDistance(lastservice, service):
    """
    En caso de que el archivo tenga un espacio en la
    distancia, se reemplaza con cero.
    """
    if service['Distance'] == '':
        service['Distance'] = 0
    if lastservice['Distance'] == '':
        lastservice['Distance'] = 0


def formatVertex(service):
    """
    Se formatea el nombrer del vertice con el id de la estación
    seguido de la ruta.
    """
    name = service['BusStopCode'] + '-'
    name = name + service['ServiceNo']
    return name
    

# ==============================
# Funciones de Comparacion
# ==============================


def compareAirportsIds(stop, keyvaluestop):

    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1