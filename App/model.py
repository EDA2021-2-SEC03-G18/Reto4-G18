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
import math 
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import orderedmap as om
from DISClib.ADT import list as lt
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import prim as pm
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
        
        analyzer['airports_directed_free'] = gr.newGraph(datastructure='ADJ_LIST',       
                                              directed=False,
                                              size=93000,
                                              comparefunction=compareAirports)
        
        analyzer['geo_index'] = om.newMap(omaptype='RBT',
                                     comparefunction=compareCoord)

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
        addGeoData(analyzer,airportinfo)
        lt.addLast(airports,airportinfo)
    
    airlines = []
    for route in input_file_routes:
        airlines = addAirportRoute(analyzer,route,airlines)
    
    cities = lt.newList()
    for cityinfo in input_file_cities:
        addCityInfo(analyzer,cityinfo)
        lt.addLast(cities, cityinfo)
    
    return totalAirports(analyzer), totalConnections(analyzer), totalAirportsDirected(analyzer), totalConnectionsDirected(analyzer), \
        totalAirportsGen(analyzer['connections_free']),totalConnectionsGen(analyzer['connections_free']),\
        totalAirportsGen(analyzer['airports_directed_free']),totalConnectionsGen(analyzer['airports_directed_free']),\
        lt.size(cities), airports, cities

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

def addGeoData(analyzer,airportinfo):
    try:
        geo_index = analyzer['geo_index']
        latitude_info = round(float(airportinfo['Latitude']),2)
        longitude_info = round(float(airportinfo['Longitude']),2)
        if om.contains(geo_index,latitude_info):
            longitude_index = om.get(geo_index,latitude_info)['value']
            if om.contains(longitude_index,longitude_info):
                list_airports = om.get(longitude_index,longitude_info)['value'] 
                lt.addLast(list_airports, airportinfo)
            else:
                list_airports = lt.newList()
                lt.addLast(list_airports,airportinfo)
                om.put(longitude_index,longitude_info,list_airports)
        else:
            longitude_index = om.newMap(omaptype='RBT', comparefunction=compareCoord)
            list_UFOs = lt.newList()
            lt.addLast(list_UFOs,airportinfo)
            om.put(longitude_index,longitude_info,list_UFOs)
            om.put(geo_index,latitude_info,longitude_index)
    except Exception as exp:
        error.reraise(exp, 'model:addGeoIndex')

def addAirport(analyzer, IATA):
    """
    Adiciona un aeropuerto como un vertice del grafo
    -- reconocido con su código IATA --
    """
    try:
        gr.insertVertex(analyzer['connections'], IATA)
        gr.insertVertex(analyzer['connections_free'], IATA)
        gr.insertVertex(analyzer['airports_directed'], IATA)
        gr.insertVertex(analyzer['airports_directed_free'], IATA)
    except Exception as exp:
        error.reraise(exp, 'model:addAirport')

def addAirportRoute(analyzer, route, airlines):
    try:
        departure = route['Departure']
        destination = route['Destination']
        distance = float(route['distance_km'])
        addRoute(analyzer, departure, destination, distance)
        addRouteFree(analyzer, departure, destination, distance)
        addAirportDirectedRoute(analyzer, departure, destination, distance)
        addAirportDirectedRouteFree(analyzer, departure, destination, distance, airlines, route['Airline'])
        return airlines
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

def addAirportDirectedRouteFree(analyzer, IATA1, IATA2, distance, airlines, airline):
    """
    Adiciona dos aeropuertos como vértices del grafo no dirigido y genera su respectiva ruta
    -- reconocido con su código IATA --
    """
    try:
        edge1 = gr.getEdge(analyzer['connections'], IATA1, IATA2)
        edge2 = gr.getEdge(analyzer['connections'], IATA2, IATA1)
        if (edge1 is not None) and (edge2 is not None) and (airline not in airlines):
            gr.addEdge(analyzer['airports_directed_free'], IATA1, IATA2, distance)
            airlines.append(airline)
    except Exception as exp:
        error.reraise(exp, 'model:addAirportDirectedRouteFree')

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
        city = cityinfo['city_ascii']
        if not m.contains(cities,city):
            homonymous_cities = lt.newList()
            lt.addLast(homonymous_cities,cityinfo)
            m.put(cities,city,homonymous_cities)
        else:
            homonymous_cities = m.get(cities,city)['value']
            lt.addLast(homonymous_cities,cityinfo) 
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

def totalAirportsGen(graph):
    """
    Retorna el total de vertices del grafo-no-dirigido
    """
    return gr.numVertices(graph)


def totalConnectionsGen(graph):
    """
    Retorna el total arcos del grafo-no-dirigido
    """
    return gr.numEdges(graph)

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
# Requerimiento 2
# ==============================
def clusterCalculation(analyzer,IATA1,IATA2):
    """
    Calcula los componentes conectados del grafo usando el algoritmo de Kosaraju
    """
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    numCluster = scc.connectedComponents(analyzer['components'])
    sameCluster = scc.stronglyConnected(analyzer['components'],IATA1,IATA2)
    return numCluster,sameCluster

# ==============================
# Requerimiento 3
# ==============================
def encounterMinimumRoute(analyzer,city_departure,city_destiny):
    geo_index = analyzer['geo_index']
    departure = encounterCloseAirport(geo_index,round(float(city_departure['lat']),2),round(float(city_departure['lng']),2))
    destiny = encounterCloseAirport(geo_index,round(float(city_destiny['lat']),2),round(float(city_destiny['lng']),2))
    analyzer['paths'] = djk.Dijkstra(analyzer['connections'], departure['IATA'])
    path = djk.pathTo(analyzer['paths'], destiny)
    return (departure,destiny,path)

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

#Gobierno Vasco -> 111.1 km = 1°
def encounterCloseAirport(latitude_index,Latitude,Longitude):
    encountered = False
    range = 10
    closest_airport = None
    minimum_distance = None
    while not encountered:
        latitude_enc = om.keys(latitude_index,Latitude-range/2,Latitude+range/2)
        if latitude_enc is not None:
            for latitude in lt.iterator(latitude_enc):
                longitude_index = om.get(latitude_index,latitude)['value']
                longitude_enc = om.keys(longitude_index,Longitude-range/2,Longitude+range/2)
                if longitude_enc is not None:
                    for longitude in lt.iterator(longitude_enc):
                        airport_list = om.get(longitude_index,longitude)['value']
                        for airportinfo in lt.iterator(airport_list):
                            distance = haversine(round(float(airportinfo['Longitude']),2),round(float(airportinfo['Latitude']),2),
                            Longitude,Latitude)
                            if minimum_distance is None:
                                minimum_distance = distance
                                closest_airport = airportinfo
                            elif minimum_distance > distance:
                                minimum_distance = distance
                                closest_airport = airportinfo
            if closest_airport is None:
                encountered = True
        else:
            range += 10

# ==============================
# Requerimiento 4
# ==============================
def createMST(analyzer):
    analyzer['search'] = pm.PrimMST(analyzer['airports_directed'])
    analyzer['prim'] = pm.prim(analyzer['airports_directed'],analyzer['search'],'LIS')


# ==============================
# Requerimiento 5
# ==============================
def evaluateClosureEffect(analyzer,IATA):
    digraph = analyzer['connections_free']
    graph = analyzer['airports_directed_free']
    degrees_digraph = gr.indegree(digraph,IATA) + gr.outdegree(digraph,IATA)
    degrees_graph = gr.indegree(graph,IATA) + gr.outdegree(graph,IATA)
    airports_affected = gr.adjacents(digraph,IATA)
    return degrees_digraph,degrees_graph,airports_affected


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

def compareCoord(coord1, coord2):
    """
    Compara dos coordenadas
    """
    if (coord1 == coord2):
        return 0
    elif (coord1 > coord2):
        return 1
    else:
        return -1
