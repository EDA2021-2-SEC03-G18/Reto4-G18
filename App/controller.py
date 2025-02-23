﻿"""
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
 """

import config as cf
import model
import csv



"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# ___________________________________________________
#  Inicializacion del catalogo
# ___________________________________________________


def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    analyzer = model.newAnalyzer()
    return analyzer

# ___________________________________________________
#  Funciones para la carga de datos y almacenamiento
#  de datos en los modelos
# ___________________________________________________


def loadInternationalRoutes(analyzer, IRfile_routes, IRfile_airports, IRfile_cities):

    IRfile_routes = cf.data_dir + IRfile_routes
    input_file_routes = csv.DictReader(open(IRfile_routes, encoding="utf-8"),
                                delimiter=",")
    
    IRfile_airports = cf.data_dir + IRfile_airports
    input_file_airports = csv.DictReader(open(IRfile_airports, encoding="utf-8"),
                                delimiter=",")
    
    IRfile_cities = cf.data_dir + IRfile_cities
    input_file_cities = csv.DictReader(open(IRfile_cities, encoding="utf-8"),
                                delimiter=",")
    
    answer = model.loadInternationalRoutes(analyzer,input_file_routes,input_file_airports,input_file_cities)

    return answer

# ___________________________________________________
#  Funciones para consultas
# ___________________________________________________


def totalAirports(analyzer):
    """
    Total de aeropuertos
    """
    return model.totalAirports(analyzer)


def totalConnections(analyzer):
    """
    Total de enlaces entre los aeropuertos
    """
    return model.totalConnections(analyzer)

def totalAirportsDirected(analyzer):
    """
    Total de aeropuertos en el grafo-no-dirigido
    """
    return model.totalAirportsDirected(analyzer)


def totalConnectionsDirected(analyzer):
    """
    Total de enlaces entre los aeropuertos en el grafo-no-dirigido
    """
    return model.totalConnectionsDirected(analyzer)

def totalCities(analyzer):
    """
    Total de ciudades en el archivo worldcities.csv y en las rutas cargadas
    """
    return model.totalCities(analyzer)

# ==============================
# Requerimiento 1
# ==============================

def top5Interconected(analyzer,airlines):
    return model.top5Interconected(analyzer,airlines)

# ==============================
# Requerimiento 2
# ==============================

def clusterCalculation(analyzer,IATA1,IATA2):
    return model.clusterCalculation(analyzer,IATA1,IATA2)

# ==============================
# Requerimiento 3
# ==============================

def requirement_three(analyzer, city_departure, city_destiny):
    return model.requirement_three(analyzer, city_departure, city_destiny)

def getCoordinates(analyzer, in_put_departure, in_put_destiny, cities_departure, cities_destiny):
    return model.getCoordinates(analyzer, in_put_departure, in_put_destiny, cities_departure, cities_destiny)

# ==============================
# Requerimiento 4
# ==============================

def calculateMST(analyzer,departure,travel_miles):
    return model.calculateMST(analyzer,departure,travel_miles)

# ==============================
# Requerimiento 5
# ==============================

def evaluateClosureEffect(analyzer,IATA):
    return model.evaluateClosureEffect(analyzer,IATA)

# ==============================
# Requerimiento 6
# ==============================
def requirement_six(analyzer, city_departure, city_destiny):
    return model.requirement_six(analyzer, city_departure, city_destiny)

def getCoordinates_r6(analyzer, in_put_departure, in_put_destiny, cities_departure, cities_destiny):
    return model.getCoordinates_r6(analyzer, in_put_departure, in_put_destiny, cities_departure, cities_destiny)

# ==============================
# Requerimiento 7
# ==============================

def get_lat_lng(data,cont):
    return model.get_lat_lng(data,cont) 