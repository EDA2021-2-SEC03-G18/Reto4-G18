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

def addAirportRoute(analyzer, route):
    try:
        departure = route['Departure']
        destination = route['Destination']
        distance = route['distance_km']
        addAirport(analyzer, departure)
        addAirport(analyzer, destination)
        addRoute(analyzer, departure, destination, distance)
        addAirportDirectedRoute(analyzer, destination, departure, distance)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addAirportRoute')

def addAirport(analyzer, IATA):
    """
    Adiciona un aeropuerto como un vertice del grafo
    -- reconocido con su código IATA --
    """
    try:
        if not gr.containsVertex(analyzer['connections'], IATA):
            gr.insertVertex(analyzer['connections'], IATA)
    except Exception as exp:
        error.reraise(exp, 'model:addAirport')

def addAirportDirectedRoute(analyzer, IATA1, IATA2, distance):
    """
    Adiciona dos aeropuertos como vértices del grafo no dirigido y genera su respectiva ruta
    -- reconocido con su código IATA --
    """
    try:
        edge = gr.getEdge(analyzer['connections'], IATA1, IATA2)
        containsIATA1 = gr.containsVertex(analyzer['airports_directed'], IATA1)
        containsIATA2 = gr.containsVertex(analyzer['airports_directed'], IATA2)
        if (edge is not None) and not(containsIATA1) and not(containsIATA2):
            gr.insertVertex(analyzer['airports_directed'], IATA1)
            gr.insertVertex(analyzer['airports_directed'], IATA2)
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

def addCityInfo(analyzer, cityinfo):
    """
    Adiciona la información pertinente de una ciudad
    """
    try:
        cities = analyzer['cities']
        city = cityinfo['city_ascii']
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
    routes = analyzer['connections']
    airports = analyzer['airports']
    cities = []
    citycount = 0 
    for IATAcode in lt.iterator(gr.vertices(routes)): 
        airport_info = m.get(airports,IATAcode)['value']
        city = airport_info['City']
        if city not in cities:
            citycount += 1
            cities.append(city)
    
    return citycount, m.size(analyzer['cities'])

def airportCityInfo(analyzer):
    routes = analyzer['connections']
    firstIATA = lt.firstElement(gr.vertices(routes))
    lastIATA = lt.lastElement(gr.vertices(routes))
    airports = analyzer['airports']
    cities = analyzer['cities']
    
    fa_info = m.get(airports,firstIATA)['value']
    la_info = m.get(airports,lastIATA)['value']
    
    listcities = m.keySet(cities)
    firstcity = lt.firstElement(listcities)
    lastcity = lt.lastElement(listcities)
    print(firstcity)
    print(lastcity)
    fc_info = m.get(cities, firstcity)['value']
    lc_info = m.get(cities, lastcity)['value']
    return [fa_info, la_info],[fc_info, lc_info]


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