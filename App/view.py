#%%
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
from DISClib.ADT import map as m
from DISClib.ADT import orderedmap as om
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
    print("3- Encontrar puntos de interconexión aérea")
    print("4- Encontrar clústeres de tráfico aéreo")
    print("5- Encontrar la ruta más corta entre ciudades")
    print("6- Utilizar las millas de viajero")
    print("7- Cuantificar el efecto de un aeropuerto cerrado")
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

def optionThree(cont):
    print("\nCalculando aeropuertos interconectados...\n")

    airport_network, top5 = controller.top5Interconected(cont)
    print('-'*80)
    print('Hay un total de', airport_network,'aeropuertos interconectados.')
    print('-'*80)
    print("\n")
    print('La información de los aeropuertos más interconectados (TOP 5) se presenta a continuación...\n')
    cont['airports']
    imprimir= PrettyTable()
    imprimir.field_names=['Name','City','Country','IATA','Connections', 'Inbound','Outbound']
    for data in lt.iterator(top5):
        imprimir.add_row([data['Name'],data['City'],data['Country'],data['IATA'],data['inbound']+data['outbound'],data['inbound'],data['outbound']])
    print(imprimir)
    print("\n")

def optionFour(cont,IATA1,IATA2):
    print("\nCalculando clúesteres en la red de transporte aéreo...\n")

    numCluster, sameCluster = controller.clusterCalculation(cont,IATA1,IATA2)
    print('-'*80)
    print('Hay un total de', numCluster,'clústeres en la red de transporte aéreo.')
    print('-'*80)
    print("\n")
    airports = cont['airports']
    print('Información de los aeropuertos 1 y 2.')
    imprimir= PrettyTable()
    imprimir.field_names=['Name', 'City','Country','Latitude','Longitude']
    airportlist = [m.get(airports,IATA1)['value'],m.get(airports,IATA2)['value']]
    for data in airportlist:
        imprimir.add_row([data['Name'],data['City'],data['Country'],round(float(data['Latitude']),2),round(float(data['Longitude']),2)])
    print(imprimir)
    print("\n")
    print('Los dos aeropuertos pertenecen al mismo clúster?')
    if sameCluster:
        Ans = 'Sí'
    else:
        Ans = 'No'
    print('R/'+Ans)

def optionFive(cont,city_departure,city_destiny):
    print("\nCalculando clúesteres en la red de transporte aéreo...\n")
    
    cities = cont['cities']
    cities_departure = m.get(cities,city_departure)['value']
    op = 1
    if lt.size(cities_departure) > 1:
        imprimir= PrettyTable()
        imprimir.field_names=['Opción','City','Country','Population''Population', 'Latitude','Longitude']
        i = 1
        for data in lt.iterator(cities_departure):
            imprimir.add_row([i,data['city_ascii'],data['country'],data['population'],round(float(data['lat']),2),round(float(data['lng']),2)])
            i += 1
        print(imprimir)
        op = int(input('Seleccione la ciudad de interés (opciones en tabla, en columna "Opción"): '))
    city_departure = lt.getElement(cities_departure,op)
    print('\n')
    cities_destiny = m.get(cities,city_destiny)['value']
    op = 1
    if lt.size(cities_destiny) > 1:
        imprimir= PrettyTable()
        imprimir.field_names=['Opción','City','Country','Population''Population', 'Latitude','Longitude']
        i = 1
        for data in lt.iterator(cities_destiny):
            imprimir.add_row([i,data['city_ascii'],data['country'],data['population'],round(float(data['lat']),2),round(float(data['lng']),2)])
            i += 1
        print(imprimir)
        op = int(input('Seleccione la ciudad de interés (opciones en tabla, en columna "Opción"): '))
    city_destiny = lt.getElement(cities_destiny,op)

    departure, destiny, path = controller.encounterMinimumRoute(cont,city_departure,city_destiny)
    
    print('Información de los aeropuertos de destino y llegada.')
    imprimir= PrettyTable()
    imprimir.field_names=['Name', 'City','Country','Latitude','Longitude']
    airportlist = [departure,destiny]
    for data in airportlist:
        imprimir.add_row([data['Name'],data['City'],data['Country'],round(float(data['Latitude']),2),round(float(data['Longitude']),2)])
    print(imprimir)

    if path is None:
        print('\nNo hay una ruta existente entre los aeropuertos más cercanos a la ciudad de destino y llegada.')
    else:
        print(path)

def optionSeven(cont,IATA):
    print("\nCalculando el efecto del cierre del aeropuerto...\n")
    
    degrees_digraph,degrees_graph,airports_affected= controller.evaluateClosureEffect(cont,IATA)
    print('-'*80)
    print('Hay un total de', degrees_digraph,'de rutas afectadas (dígrafo).')
    print('Hay un total de', degrees_graph,'de rutas afectadas (grafo-no-dirigido).\n')
    print('Hay un total de', lt.size(airports_affected), 'de aeropuertos afectados.')
    print('-'*80)
    print("\n")
    airports = cont['airports']
    print('Información de los aeropuertos.')
    if lt.size(airports_affected) > 6:
        imprimir= PrettyTable()
        imprimir.field_names=['Name', 'City','Country','Latitude','Longitude']
        first_elements = lt.subList(airports_affected,1,3)
        for airport in lt.iterator(first_elements):
            data = m.get(airports,airport)['value']
            imprimir.add_row([data['Name'],data['City'],data['Country'],round(float(data['Latitude']),2),round(float(data['Longitude']),2)])
        
        last_elements = lt.subList(airports_affected,lt.size(airports_affected)-2,3)
        for airport in lt.iterator(last_elements):
            data = m.get(airports,airport)['value']
            imprimir.add_row([data['Name'],data['City'],data['Country'],round(float(data['Latitude']),2),round(float(data['Longitude']),2)])
        print(imprimir)
    elif lt.size(airports_affected) > 0:
        imprimir= PrettyTable()
        imprimir.field_names=['Name', 'City','Country','Latitude','Longitude']
        for airport in lt.iterator(airports_affected):
            data = m.get(airports,airport)['value']
            imprimir.add_row([data['Name'],data['City'],data['Country'],round(float(data['Latitude']),2),round(float(data['Longitude']),2)])
        print(imprimir)


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
        
        elif int(inputs[0]) == 3:
            optionThree(cont)
            input('Presione "Enter" para continuar.\n')
        elif int(inputs[0]) == 4:
            IATA1 = input('Ingrese el código IATA del primer aeropuerto: ')
            IATA2 = input('Ingrese el código IATA del segundo aeropuerto: ')
            optionFour(cont,IATA1,IATA2)
            input('Presione "Enter" para continuar.\n')
        elif int(inputs[0]) == 5:
            city_departure = input('Ingrese la ciudad de destino: ')
            city_destiny = input('Ingrese la ciudad de llegada: ')
            optionFive(cont,city_departure,city_destiny)
            input('Presione "Enter" para continuar.\n')
        elif int(inputs[0]) == 6:
            controller.createMST(cont)
            print(cont['search']['edgeTo'])
            print(cont['prim'])
            input('Presione "Enter" para continuar.\n')
        elif int(inputs[0]) == 7:
            IATAcode = input('Ingrese el código IATA del aeropuerto a eliminar: ')
            optionSeven(cont,IATAcode)
            input('Presione "Enter" para continuar.\n')
        else:
            sys.exit(0)
    sys.exit(0)

if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()

# %%
