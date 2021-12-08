"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
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

import sys
import config as cf
import threading
from App import controller
from DISClib.ADT import stack
from DISClib.ADT import list as lt
assert cf 
from prettytable import PrettyTable

"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

# ___________________________________________________
#  Variables
# ___________________________________________________


IRfile_airports = 'airports-utf8-small.csv'
IRfile_routes= "routes-utf8-small.csv"
IRfile_worldcities= "worldcities-utf8.csv"
initialStation = None

# ___________________________________________________
#  Menu principal
# ___________________________________________________

def printMenu():
    print("\n")
    print("*******************************************")
    print("Bienvenido")
    print("1- Inicializar Analizador")
    print("2- Cargar información de la red de transporte aéreo")
    print("0- Salir")
    print("*******************************************")



def optionTwo(cont):
    print("\nCargando información...\n")
    
    numvertex, numedges, numvertex_directed, numedges_directed, citycount, airports, cities = controller.loadInternationalRoutes(cont, IRfile_routes, IRfile_airports, IRfile_worldcities)
    print('-'*80)
    print('Número de aeropuertos - nodos - (dígrafo): ' + str(numvertex))
    print('Número de rutas aéreas - arcos - (dígrafo): ' + str(numedges))
    print('\nNúmero de aeropuertos - nodos - (grafo-no-dirigido): ' + str(numvertex_directed))
    print('Número de rutas aéreas - arcos - (grafo-no-dirigido): ' + str(numedges_directed))
    print('\nNúmero de ciudades: ' + str(citycount))
    imprimir= PrettyTable()
    imprimir.field_names=['Name', 'City','Country','Latitude','Longitude']
    airportlist = [lt.firstElement(airports),lt.lastElement(airports)]
    for data in airportlist:
        imprimir.add_row([data['Name'],data['City'],data['Country'],round(float(data['Latitude']),2),round(float(data['Longitude']),2)])
    print(imprimir)
    print("\n")
    imprimir= PrettyTable()
    citylist = [lt.firstElement(cities),lt.lastElement(cities)]
    imprimir.field_names=['City','Country','Population''Population', 'Latitude','Longitude']
    for data in citylist:
        imprimir.add_row([data['city_ascii'],data['country'],data['population'],round(float(data['lat']),2),round(float(data['lng']),2)])
    print(imprimir)
    print("\n")
    print('El limite de recursión actual: ' + str(sys.getrecursionlimit()))
    print('-'*80)

"""
Menú principal
"""
def thread_cycle():
    while True:
        printMenu()
        inputs = input('Seleccione una opción para continuar\n>')

        if int(inputs[0]) == 1:
            print("\nInicializando....")
            cont = controller.init()

        elif int(inputs[0]) == 2:
            optionTwo(cont)
            input('Presione "Enter" para continuar.\n')

        else:
            sys.exit(0)
    sys.exit(0)

if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()