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



from branca.element import Element
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
from DISClib.ADT import stack as s
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import prim as pm
from DISClib.Utils import error as error
assert config
from haversine import haversine, Unit 
import folium
import json 


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
        
        analyzer['airports_affected'] = m.newMap(numelements=93000,
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
        addAirportAffected(analyzer,airportinfo['IATA'])
        addGeoData(analyzer,airportinfo)
        lt.addLast(airports,airportinfo)
    
    airlines = []
    routes = []
    for route in input_file_routes:
        addAirportAffectedValue(analyzer,route,routes)
        airlines = addAirportRoute(analyzer,route,airlines)
        routes.append(route['Departure']+'-'+route['Destination'])
    
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
def top5Interconected(analyzer,airlines):
    if airlines:
        digraph = analyzer['connections_free']
    else:
        digraph = analyzer['connections']
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

#############################################################
def requirement_three(analyzer, city_departure, city_destiny):
    try:
        getCitiesByCity_1=getCitiesByCity1(analyzer, city_departure)
        getCitiesByCity_2=getCitiesByCity2(analyzer, city_destiny)
        return (getCitiesByCity_1, getCitiesByCity_2)
    except Exception as exp:
        error.reraise(exp, 'model:requirement_three')
#############################################################
def getCitiesByCity1(analyzer, city):
    try:
        existence = m.contains(analyzer['cities'], city)
        if existence:
            cities = m.get(analyzer['cities'], city)["value"]
            return cities
        return None
    except Exception as exp:
        error.reraise(exp, 'model:getCitiesByCity1')
#############################################################
def getCitiesByCity2(analyzer, city):
    try:
        existence = m.contains(analyzer['cities'], city)
        if existence:
            cities = m.get(analyzer['cities'], city)["value"]
            return cities
        return None
    except Exception as exp:
        error.reraise(exp, 'model:getCitiesByCity2')
#############################################################
def getCoordinates(analyzer, in_put_departure, in_put_destiny, cities_departure, cities_destiny):
    try:
        choice_1= int(in_put_departure)
        count1= 1
        for element in lt.iterator(cities_departure):
         
            if count1==choice_1:
                city_departureinfo=float(element["lat"]),float(element["lng"])
                break
            count1 += 1
        choice_2= int(in_put_destiny)
        count2=1
        for element in lt.iterator(cities_destiny):
            if count2==choice_2:
                city_destinyinfo=float(element["lat"]),float(element["lng"])
                break
            count2 += 1
         
        H1= haversine_r3(analyzer, city_departureinfo)
        H2= haversine_r3(analyzer, city_destinyinfo)
        I_need_all= route_short(analyzer, H1[0], H2[0])
        return (I_need_all, H1, H2)
        
    except Exception as exp:
        error.reraise(exp, 'model:getCoordinates')
#############################################################
def haversine_r3(analyzer, city_departureinfo):
    """
        Calculate the great circle distance in kilometers between two points 
        on the earth (specified in decimal degrees)
        """
    try:
        min= 99**(19)
        info= ""
        cities= analyzer['airports']
        valueSet_cities= m.valueSet(cities)
        for element in lt.iterator(valueSet_cities):
            latitude_longitude=float(element["Latitude"]), float(element["Longitude"])
            Haversine= haversine(city_departureinfo, latitude_longitude, unit=Unit.KILOMETERS)
            if Haversine<min:
                min=Haversine
                info= element
        return info, min
    except Exception as exp:
        error.reraise(exp, "model:haversine_r3")
#############################################################
def route_short(analyzer, H1, H2):
    try:
        digraph= analyzer["connections"]
        airport_H1= H1["IATA"]
        airport_H2= H2["IATA"]
        route_s= djk.Dijkstra(digraph, airport_H1)
        distance_airports=djk.distTo(route_s, airport_H2)
        if djk.hasPathTo(route_s, airport_H2):
            I_need_all= djk.pathTo(route_s, airport_H2)
            return  I_need_all, distance_airports
    except Exception as exp:
        error.reraise(exp, "model:route_short")

# ==============================
# Requerimiento 4
# ==============================
def calculateMST(analyzer,departure,travel_miles):
    MST_structure = pm.PrimMST(analyzer['airports_directed'])['edgeTo']
    longest_distance = 0
    total_MST_cost = 0
    list_flight = lt.newList()
    map_info = m.newMap()
    known_sites = m.newMap()
    
    ordered_values = s.newStack()
    
    #DataStructureConstructed
    for key in lt.iterator(m.keySet(MST_structure)):
        flight_info = m.get(MST_structure,key)['value']
        IATAcode1 = flight_info['vertexA']
        IATAcode2 = flight_info['vertexB']
        distance = flight_info['weight']
        total_MST_cost += distance
        if m.get(map_info,IATAcode1) is None:
            sites = lt.newList()
            lt.addLast(sites,{'site':IATAcode2,'dist':distance})
            datastructure = {'sites':sites,'pos':1}
            m.put(map_info,IATAcode1,datastructure)
        else:
            IATAinfo = m.get(map_info,IATAcode1)['value']
            lt.addLast(IATAinfo['sites'],{'site':IATAcode2,'dist':distance})
        
        if m.get(map_info,IATAcode2) is None:
            sites = lt.newList()
            lt.addLast(sites,{'site':IATAcode1,'dist':distance})
            datastructure = {'sites':sites,'pos':1}
            m.put(map_info,IATAcode2,datastructure)
        else:
            IATAinfo = m.get(map_info,IATAcode2)['value']
            lt.addLast(IATAinfo['sites'],{'site':IATAcode1,'dist':distance})
    
    #Longest branch and total cost in km
    s.push(ordered_values,departure)
    IATAinfo = m.get(map_info,departure)['value']
    IATAcode1 = departure
    order = 1
    arrived = False
    while not arrived:
        if s.top(ordered_values) != departure or (order == 1):
            if IATAinfo['pos'] <= lt.size(IATAinfo['sites']):
                IATAinfo2 = lt.getElement(IATAinfo['sites'],IATAinfo['pos'])
                IATAcode2 = IATAinfo2['site']
                distance = IATAinfo2['dist']
                if ((m.get(known_sites,IATAcode1 +'-'+ IATAcode2) is not None) or (m.get(known_sites,IATAcode2 +'-'+ IATAcode1) is not None)) and (IATAinfo['pos'] <= lt.size(IATAinfo['sites'])):
                    IATAinfo['pos'] += 1
                elif IATAinfo['pos'] <= lt.size(IATAinfo['sites']):
                    longest_distance += distance
                    IATAinfo['pos'] += 1
                    if m.get(known_sites,IATAcode1 +'-'+ IATAcode2) is None and m.get(known_sites,IATAcode2 +'-'+ IATAcode1) is None:
                        lt.addLast(list_flight,{'site1':IATAcode1,'site2':IATAcode2,'dist':distance})
                        order += 1
                    m.put(known_sites,IATAcode1+'-'+IATAcode2,order)
                    s.push(ordered_values,IATAcode2)
                    IATAcode1 = IATAcode2
                else:
                    s.pop(ordered_values)
                    IATAcode1 = s.top(ordered_values)
            else:
                s.pop(ordered_values)
                IATAcode1 = s.top(ordered_values)
            IATAinfo = m.get(map_info,IATAcode1)['value']
        else:
            arrived = True
    
    return longest_distance,total_MST_cost,(longest_distance*2-travel_miles*1.6)/1.6,list_flight


# ==============================
# Requerimiento 5
# ==============================
def addAirportAffected(analyzer, IATA):
    """
    Adiciona aeropuertos afectados a la estructura de almacenamiento para estos
    """
    try:
        airports = analyzer['airports_affected']
        IATAcode = IATA
        m.put(airports,IATAcode,{'Digraph':0,'Graph':0})
    except Exception as exp:
        error.reraise(exp, 'model:addAirportInfo')

def addAirportAffectedValue(analyzer, routeinfo,routes):
    """
    Adiciona información de los aeropuertos afectados
    """
    try:
        airports = analyzer['airports_affected']
        IATAcode1 = routeinfo['Departure']
        IATAcode2 = routeinfo['Destination']
        values1 = m.get(airports,IATAcode1)['value']
        values1['Digraph'] += 1
        if (routeinfo['Destination']+'-'+routeinfo['Departure'] in routes) and (routeinfo['Departure']+'-'+routeinfo['Destination'] not in routes):
            values1['Graph'] += 1

        values2 = m.get(airports,IATAcode2)['value']
        values2['Digraph'] += 1
        if (routeinfo['Destination']+'-'+routeinfo['Departure'] in routes) and (routeinfo['Departure']+'-'+routeinfo['Destination'] not in routes):
            values2['Graph'] += 1
    except Exception as exp:
        error.reraise(exp, 'model:addAirportInfo')
def evaluateClosureEffect(analyzer,IATA):
    digraph = analyzer['connections_free']
    airports = analyzer['airports']
    airports_affected = analyzer['airports_affected']
    degrees_digraph = m.get(airports_affected,IATA)['value']['Digraph']
    degrees_graph = m.get(airports_affected,IATA)['value']['Graph']
    airports_affected = gr.adjacents(digraph,IATA)
    if lt.size(airports_affected) > 0:
        known_airports = []
        airports_map = om.newMap(omaptype='RBT',comparefunction=compareIATA)
        for airport in lt.iterator(airports_affected):
            if airport not in known_airports:
                known_airports.append(airport)
                om.put(airports_map,airport,m.get(airports,airport)['value'])
        
        ans_airports_affected = lt.newList()
        if om.size(airports_map) > 6:
            lowest_IATA = om.minKey(airports_map)
            highest_IATA = om.maxKey(airports_map)
            lt.addLast(ans_airports_affected,om.get(airports_map,lowest_IATA)['value'])
            lt.addLast(ans_airports_affected,om.get(airports_map,highest_IATA)['value'])
            t = 1
            for i in range(2):
                om.deleteMin(airports_map)
                om.deleteMax(airports_map)
                lowest_IATA = om.minKey(airports_map)
                highest_IATA = om.maxKey(airports_map)
                lt.insertElement(ans_airports_affected,om.get(airports_map,lowest_IATA)['value'],i)
                lt.addLast(ans_airports_affected,om.get(airports_map,highest_IATA)['value'],lt.size(ans_airports_affected)-t)
                t += 1
        else:
            for key in lt.iterator(om.keySet(airports_map)):
                lt.addLast(ans_airports_affected,om.get(airports_map,key)['value'])

        return degrees_digraph,degrees_graph,ans_airports_affected
    else:
        return None



# ==============================
# Requerimiento 6
# ==============================

#############################################################
def requirement_six(analyzer, city_departure, city_destiny):
    try:
        getCitiesByCity_1=getCitiesByCity1_r6(analyzer, city_departure)
        getCitiesByCity_2=getCitiesByCity2_r6(analyzer, city_destiny)
        return (getCitiesByCity_1, getCitiesByCity_2)
    except Exception as exp:
        error.reraise(exp, 'model:requirement_three')
#############################################################
def getCitiesByCity1_r6(analyzer, city):
    try:
        existence = m.contains(analyzer['cities'], city)
        if existence:
            cities = m.get(analyzer['cities'], city)["value"]
            return cities
        return None
    except Exception as exp:
        error.reraise(exp, 'model:getCitiesByCity1')
#############################################################
def getCitiesByCity2_r6(analyzer, city):
    try:
        existence = m.contains(analyzer['cities'], city)
        if existence:
            cities = m.get(analyzer['cities'], city)["value"]
            return cities
        return None
    except Exception as exp:
        error.reraise(exp, 'model:getCitiesByCity2_r6')
#############################################################
def getCoordinates_r6(analyzer, in_put_departure, in_put_destiny, cities_departure, cities_destiny):
    try:
        choice_1= int(in_put_departure)
        count1= 1
        for element in lt.iterator(cities_departure):
         
            if count1==choice_1:
                city_departureinfo=float(element["lat"]),float(element["lng"])
                break
            count1 += 1
        choice_2= int(in_put_destiny)
        count2=1
        for element in lt.iterator(cities_destiny):
            if count2==choice_2:
                city_destinyinfo=float(element["lat"]),float(element["lng"])
                break
            count2 += 1
         
        H1= haversine_r6(city_departureinfo)
        H2= haversine_r6(city_destinyinfo)
        I_need_all= route_short_r6(analyzer, H1[0], H2[0])
        return (I_need_all, H1, H2)
        
    except Exception as exp:
        error.reraise(exp, 'model:getCoordinates_r6')
#############################################################
def haversine_r6(city_departureinfo):
    """
        Calculate the great circle distance in kilometers between two points 
        on the earth (specified in decimal degrees)
        """
    try:
        min= 99**(19)
        info= ""
        with open("Data/AirportNearestRelevant_v1_Version_1.0_swagger_specification.json") as contenido:
            c= json.load(contenido)
            d= (c)["responses"]
            e= d["nearest-relevant-airports"]
            f= e["schema"]
            g= f["example"]
            h= g["data"]
            for element in h: #Pasa o abre las carpetas de 0-09
                geocode=element["geoCode"]
                analytics= element["analytics"]
                flights= analytics["flights"]
                address= element["address"]
                
                latitude= geocode["latitude"]
                longitude= geocode["longitude"]
                score= flights["score"]
                IATA= element["iataCode"]
                name= element["name"]
                cityName= address["cityName"]
                countryName= address["countryName"]

                latitude_longitude=float(latitude), float(longitude)
                Haversine= haversine(city_departureinfo, latitude_longitude, unit=Unit.KILOMETERS)
                if Haversine<min:
                    min=Haversine  #menor distancia
                    info= (IATA, name, score, cityName, countryName, latitude, longitude)  #información
            return info, min
    except Exception as exp:
        error.reraise(exp, "model:haversine_r6")
#############################################################
def route_short_r6(analyzer, H1, H2):
    try:
        digraph= analyzer["connections"]
        airport_H1= str(H1[0])
        airport_H2= str(H2[0])
        t1= float(H1[5]), float(H1[6])
        t2= float(H2[5]), float(H2[6])

        if gr.containsVertex(digraph, airport_H1):
            route_s= djk.Dijkstra(digraph, airport_H1)
            distance_airports=djk.distTo(route_s, airport_H2)
            if djk.hasPathTo(route_s, airport_H2):
                I_need_all= djk.pathTo(route_s, airport_H2)
                return  I_need_all, distance_airports
        else:
            distance_airports=haversine(t1, t2, unit=Unit.KILOMETERS)
            I_need_all=None
            return  I_need_all, distance_airports

    except Exception as exp:
        error.reraise(exp, "model:route_short_r6")



# ==============================
# Requerimiento 7
# ==============================


#REQUERIMIENTO 1 MAPA 
#--------------------------------
def get_lat_lng(data,analyzer):
    IATA= data["IATA"]
    info=m.get(analyzer["airports"],IATA)['value']
    LAT= info["Latitude"]
    LNG= info["Longitude"]
    return LAT, LNG



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

def compareIATA(IATA1, IATA2):
    """
    Compara dos coordenadas
    """
    if (IATA1 == IATA2):
        return 0
    elif (IATA1 > IATA2):
        return 1
    else:
        return -1