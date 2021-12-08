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
from DISClib.ADT import orderedmap as om
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
    """ Inicializa el analizador

    airports: Tabla de hash para guardar la información de los aeropuertos
    IATAs: Tabla de hash para guardar los vértices del grafo
    connections: Grafo para representar los vuelos entre aeropuertos
    airports_directed: Grafo no dirigido para representar  exclusivamente 
    los vuelos entre aeropuertos con conexión de ida y vuelta entre sí
    Almacena la informacion de los componentes conectados
    paths: Estructura que almancena las rutas de costo mínimo desde un
            vértice determinado (aeropuerto) a todos los otros vértices del grafo
    """
    try:
        analyzer = {
                    'airports': None,
                    'cities': None,
                    'connections': None,
                    'connections_free': None,
                    'airports_directed': None
                    }

        analyzer['airports'] = m.newMap(numelements=93000,
                                     maptype='PROBING',
                                     comparefunction=compareAirports)
        
        analyzer['cities'] = m.newMap(numelements=93000,
                                     maptype='PROBING',
                                     comparefunction=compareAirports)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=93000,
                                              comparefunction=compareAirports)
        
        analyzer['connections_free'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=93000,
                                              comparefunction=compareAirports)


        analyzer['airports_directed'] = gr.newGraph(datastructure='ADJ_LIST',       
                                              directed=False,
                                              size=93000,
                                              comparefunction=compareAirports)

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')




# ==============================
# Funciones de consulta
# ==============================

# ==============================
# Carga de datos
# ==============================
def loadInternationalRoutes(analyzer, input_file_routes, input_file_airports, input_file_cities):
    
    airports = lt.newList()
    for airportinfo in input_file_airports:
        addAirportInfo(analyzer,airportinfo)
        addAirport(analyzer,airportinfo['IATA'])
        lt.addLast(airports,airportinfo)

    for route in input_file_routes:
        addAirportRoute(analyzer,route)
    
    cities = lt.newList()
    for cityinfo in input_file_cities:
        addCityInfo(analyzer,cityinfo)
        lt.addLast(cities, cityinfo)
    
    return totalAirports(analyzer), totalConnections(analyzer), totalAirportsDirected(analyzer), totalConnectionsDirected(analyzer), totalCities(analyzer), airports, cities

def addAirportInfo(analyzer, airportinfo):
    """
    Adiciona la información pertinente de un aeropuerto
    """
    try:
        airports = analyzer['airports']
        IATAcode = airportinfo['IATA']
        m.put(airports,IATAcode,airportinfo)
    except Exception as exp:
        error.reraise(exp, 'model:addAirportInfo')

def addAirport(analyzer, IATA):
    """
    Adiciona un aeropuerto como un vertice del grafo
    -- reconocido con su código IATA --
    """
    try:
        gr.insertVertex(analyzer['connections'], IATA)
        gr.insertVertex(analyzer['connections_free'], IATA)
        gr.insertVertex(analyzer['airports_directed'], IATA)
    except Exception as exp:
        error.reraise(exp, 'model:addAirport')

def addAirportRoute(analyzer, route):
    try:
        departure = route['Departure']
        destination = route['Destination']
        distance = route['distance_km']
        addRoute(analyzer, departure, destination, distance)
        addRouteFree(analyzer, departure, destination, distance)
        addAirportDirectedRoute(analyzer, departure, destination, distance)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addAirportRoute')

def addAirportDirectedRoute(analyzer, IATA1, IATA2, distance):
    """
    Adiciona dos aeropuertos como vértices del grafo no dirigido y genera su respectiva ruta
    -- reconocido con su código IATA --
    """
    try:
        edge1 = gr.getEdge(analyzer['connections'], IATA1, IATA2)
        edge2 = gr.getEdge(analyzer['connections'], IATA2, IATA1)
        edge = gr.getEdge(analyzer['airports_directed'], IATA1, IATA2)
        if (edge1 is not None) and (edge2 is not None) and (edge is None):
            gr.addEdge(analyzer['airports_directed'], IATA1, IATA2, distance)
    except Exception as exp:
        error.reraise(exp, 'model:addAirportDirectedRoute')

def addRoute(analyzer, departure, destination, distance):
    """
    Adiciona un arco entre dos aeropuertos
    """
    try:
        edge = gr.getEdge(analyzer['connections'], departure, destination)
        if edge is None:
            gr.addEdge(analyzer['connections'], departure, destination, distance)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addRoute')

def addRouteFree(analyzer, departure, destination, distance):
    """
    Adiciona un arco entre dos aeropuertos
    """
    try:
        gr.addEdge(analyzer['connections_free'], departure, destination, distance)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addRoute')

def addCityInfo(analyzer, cityinfo):
    """
    Adiciona la información pertinente de una ciudad
    """
    try:
        cities = analyzer['cities']
        city = cityinfo['id']

        m.put(cities,city,cityinfo)
    except Exception as exp:
        error.reraise(exp, 'model:addCityInfo')

def totalAirports(analyzer):
    """
    Retorna el total de vertices del dígrafo
    """
    return gr.numVertices(analyzer['connections'])


def totalConnections(analyzer):
    """
    Retorna el total arcos del dígrafo 
    """
    return gr.numEdges(analyzer['connections'])

def totalAirportsDirected(analyzer):
    """
    Retorna el total de vertices del grafo-no-dirigido
    """
    return gr.numVertices(analyzer['airports_directed'])


def totalConnectionsDirected(analyzer):
    """
    Retorna el total arcos del grafo-no-dirigido
    """
    return gr.numEdges(analyzer['airports_directed'])

def totalCities(analyzer):
    return m.size(analyzer['cities'])

# ==============================
# Requerimiento 1
# ==============================
def top5Interconected(analyzer):
    digraph = analyzer['connections_free']
    airport_map = analyzer['airports']
    airports = gr.vertices(digraph)
    airports_connections = om.newMap(omaptype='RBT',comparefunction= compareconnections)
    airport_network = 0
    for airport in lt.iterator(airports):
        outbound = gr.outdegree(digraph,airport)
        inbound = gr.indegree(digraph,airport)
        connections = outbound+inbound
        if connections > 0:
            airport_network += 1
        airportinfo = m.get(airport_map,airport)['value']
        airportinfo['outbound'] = outbound
        airportinfo['inbound'] = inbound
        if not om.contains(airports_connections,connections):
            airports_list = lt.newList()
            lt.addLast(airports_list,airportinfo)
            om.put(airports_connections,connections,airports_list)
        else:
            airports_list = om.get(airports_connections,connections)['value']
            lt.addLast(airports_list,airportinfo)
    top5 = lt.newList()
    maxKey = om.maxKey(airports_connections)
    airports_max = om.get(airports_connections,maxKey)['value']

    while lt.size(top5)<5:
        i = 1
        while lt.size(top5) < 5 and i <= lt.size(airports_max):
            airportinfo = lt.getElement(airports_max,i)
            lt.addLast(top5,airportinfo)
            i += 1
        
        om.deleteMax(airports_connections)
        maxKey = om.floor(airports_connections,maxKey)
        airports_max = om.get(airports_connections,maxKey)['value']
    
    return airport_network, top5

# ==============================
# Funciones de Comparacion
# ==============================


def compareAirports(airport, keyvalueairport):

    airportcode = keyvalueairport['key']
    if (airport == airportcode):
        return 0
    elif (airport > airportcode):
        return 1
    else:
        return -1

def compareroutes(route1, route2):
    """
    Compara dos rutas
    """
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1

def compareconnections(connections1, connections2):
    """
    Compara dos rutas
    """
    if (connections1 == connections2):
        return 0
    elif (connections1 > connections2):
        return 1
    else:
        return -1
# %%
