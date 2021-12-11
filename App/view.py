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
from DISClib.Algorithms.Graphs import dijsktra as djk
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
    
    numvertex, numedges, numvertex_directed, numedges_directed, numvertex_free, numedges_free,numvertex_directed_free, numedges_directed_free, citycount, airports, cities = controller.loadInternationalRoutes(cont, IRfile_routes, IRfile_airports, IRfile_worldcities)
    print('-'*80)
    print('Número de aeropuertos - nodos - (dígrafo): ' + str(numvertex))
    print('Número de rutas aéreas - arcos - (dígrafo): ' + str(numedges))
    print('\nNúmero de aeropuertos - nodos - (grafo-no-dirigido): ' + str(numvertex_directed))
    print('Número de rutas aéreas - arcos - (grafo-no-dirigido): ' + str(numedges_directed))
    print('\nNúmero de aeropuertos - nodos - (dígrafo con aerolíneas): ' + str(numvertex_free))
    print('Número de rutas aéreas - arcos - (dígrafo con aerolíneas): ' + str(numedges_free))
    print('\nNúmero de aeropuertos - nodos - (grafo-no-dirigido con aerolíneas): ' + str(numvertex_directed_free))
    print('Número de rutas aéreas - arcos - (grafo-no-dirigido con aerolíneas): ' + str(numedges_directed_free))
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


def optionFive(coordinates):
    print('-'*80)
    print("Ciudad de partida: "+ coordinates[1][0]["City"])
    print("Ciudad de destino: "+coordinates[2][0]["City"])
    print('-'*80)

    print("El aeropuerto de patidad en "+(coordinates[1][0])["City"]+ " es...")
    imprimir= PrettyTable()
    imprimir.field_names=['IATA', 'Name','City','Country']
    imprimir.add_row([coordinates[1][0]['IATA'],coordinates[1][0]['Name'],coordinates[1][0]['City'],coordinates[1][0]['Country']])
    print(imprimir)
    print("\n")
    print("El aeropuerto de llegada en "+(coordinates[2][0])["City"]+ " es...")
    imprimir= PrettyTable()
    imprimir.field_names=['IATA', 'Name','City','Country']
    imprimir.add_row([coordinates[2][0]['IATA'],coordinates[2][0]['Name'],coordinates[2][0]['City'],coordinates[2][0]['Country']])
    print(imprimir)
    print("\n")
    print("="*80)
    total_distance= float(coordinates[1][1]) + float(coordinates[2][1]) + float(coordinates[0][1])
    print("\n")
    print("La distancia total : "+ str(total_distance)+" Km.")
    imprimir= PrettyTable()
    imprimir.field_names=['Departure', 'Destination','distance_km']
    si_ze_1= stack.size(coordinates[0][0])
    n=1
    while n <= si_ze_1:
        element= stack.pop(coordinates[0][0])
        imprimir.add_row([element["vertexA"],element["vertexB"],element["weight"]])
        n +=1
    print(imprimir)

    



def optionSeven(cont,IATA):
    print("\nCalculando el efecto del cierre del aeropuerto...\n")

    degrees_digraph,degrees_graph,airports_affected= controller.evaluateClosureEffect(cont,IATA)
    known_airports = []
    i = 1
    while i < lt.size(airports_affected):
        airport = lt.getElement(airports_affected,i)
        if airport not in known_airports:
            known_airports.append(airport)
        else:
            lt.deleteElement(airports_affected,i)
        i += 1
    print('-'*80)
    print('Hay un total de', degrees_digraph,'de rutas afectadas (dígrafo).')
    print('Hay un total de', degrees_graph,'de rutas afectadas (grafo-no-dirigido).\n')
    print('Hay un total de', lt.size(airports_affected), 'de aeropuertos afectados.')
    print('-'*80)
    print("\n")
    airports = cont['airports']
    print('Información de los aeropuertos afectados.')

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
            print("-"*80)
            city_departure = input('Ingrese la ciudad de partida (Por ejemplo, "Saint Petersburg"): ')
            city_destiny = input('Ingrese la ciudad de destino (Por ejemplo, "Lisbon"): ')
            print("-"*80)
            print("\n")
            CitiesByCity= controller.requirement_three(cont, city_departure, city_destiny)
            print("Decida en qué país se encuentra la ciudad "+ city_departure+ " e ingrese un número entero en el orden en que se muestra las opciones en la tabla.")
            imprimir= PrettyTable()
            imprimir.field_names=["No.",'city', 'country','lat','lng', "capital", "population"]
            n=1
            for element in lt.iterator(CitiesByCity[0]):
                imprimir.add_row([(n),element['city'],element['country'],element['lat'],element['lng'], element['capital'],element['population']])
                n +=1
            print(imprimir)
            print("\n")
            in_put_departure= input("Ingrese su elección (un entero) para la ciudad de partida: ")
            print("-"*80)
            print("Decida en qué país se encuentra la ciudad "+city_destiny+ " e ingrese un número entero en el orden en que se muestra las opciones en la tabla.")
            imprimir= PrettyTable()
            imprimir.field_names=["No.",'city', 'country','lat','lng', "capital", "population"]
            h=1
            for element in lt.iterator(CitiesByCity[1]):
                imprimir.add_row([(h),element['city'],element['country'],element['lat'],element['lng'], element['capital'],element['population']])
                h += 1
            print(imprimir)
            print("\n")
            in_put_destiny= input("Ingrese su elección (un entero) para la ciudad de destino: ")
            coordinates=controller.getCoordinates(cont, in_put_departure, in_put_destiny, CitiesByCity[0], CitiesByCity[1])
            optionFive(coordinates)
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

