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
    
    for route in input_file_routes:
        model.addAirportRoute(analyzer,route)
    
    for airportinfo in input_file_airports:
        model.addAirportInfo(analyzer,airportinfo)
    
    for cityinfo in input_file_cities:
        model.addCityInfo(analyzer,cityinfo)
    
    return analyzer

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

def airportCityInfo(analyzer):
    """
    Información de las primer@s y últim@s aeropuertos/ciudades cargad@s 
    """
    return model.airportCityInfo(analyzer)