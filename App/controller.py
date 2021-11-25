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


def loadServices(analyzer,  servicesfile_airports, servicesfile_routes):

    servicesfile_airports = cf.data_dir + servicesfile_airports
    input_file_airports = csv.DictReader(open(servicesfile_airports, encoding="utf-8"),
                                delimiter=",")
    servicesfile_routes = cf.data_dir + servicesfile_routes
    input_file_routes = csv.DictReader(open(servicesfile_routes, encoding="utf-8"),
                                delimiter=",")
    lastservice = None
    for service in input_file_routes:
        if lastservice is not None:
            samedestination= lastservice['Destination'] == service['Destination']
            samedeparture = lastservice['Departure'] == service['Departure']
            if samedeparture and not samedestination:
                model.addStopConnection(analyzer, lastservice, service)
            lastservice = service

    model.addRouteConnections(analyzer)
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
