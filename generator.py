import random, csv

def generar_instancias():
    filas=[]

    #datos para la generación del dataset
    instancias_arr=["peq", "med", "gra"]
    dias_arr=["5,7", "7,14", "14,28"]
    trabajadores_arr=["5,15", "15,45", "45,90"]
    turnos_arr=["dia,noche", "manana,tarde,noche", "manana,tarde,noche"]
    semana_dias=["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

    for ins in instancias_arr: #una iteración para cada tipo de instancia
        index=instancias_arr.index(ins)

        dias_range=dias_arr[index]
        coma_idx_dias=dias_range.index(',')
        
        trabajadores_range=trabajadores_arr[index]
        coma_idx_trabs=trabajadores_range.index(',')

        turnos=turnos_arr[index].split(',')

        i=0
        while (i<5): #cinco instancias para cada tipo de instancia
            #generamos cada una de las instancias
            cantidad_turnos=len(turnos)
            dias=random.randint(int(dias_range[:coma_idx_dias]), int(dias_range[coma_idx_dias+1:]))
            trabajadores=random.randint(int(trabajadores_range[:coma_idx_trabs]), int(trabajadores_range[coma_idx_trabs+1:]))

            #iteramos cada día de la instancia y generamos la demanda de sus turnos
            demanda_dias={}
            j=0
            indicador=0
            while (j<dias):
                #seleccionamos día de la semana
                semana_dia=semana_dias[j%7]
                
                if(j%7==0): #cada vez que damos una vuelta a la semana...
                    indicador+=1

                #generar la demanda para cada turno del día
                demandas_turnos=[]
                for turno in turnos:
                    mu = (trabajadores/cantidad_turnos) * random.uniform(1.0, 1.2) #la mediana (mu) de nuestra normalvariate() será este cociente para que las demandas sean repartidas casi equitativamente. Luego, multiplicamos por un valor el cual aumentará levemente la demanda de ese turno con tal de lograr ciertos desvíos y que la demanda total del día pueda ser también infactible, no solo factible
                    sigma = mu*0.2 #para que la desviación sea proporicional a mu. 0.2 será un número arbitrario, para que la desviación sea de un 20% de mu, lo cual es suficiente para hacer diferencias significativas pero no tan grande para desviar demasiado los valores.

                    demanda_turno=int(random.normalvariate(mu, sigma))
                    demandas_turnos.append([turno, demanda_turno])

                #añadimos al diccionario de días
                nombre_key=semana_dia+"_"+str(indicador)
                demanda_dias[nombre_key] = demandas_turnos

                j+=1

            filas.append([ins, dias, trabajadores, demanda_dias]) #terminamos la instancia
            i+=1

    return filas

def main():
    data=generar_instancias()
    nombre_archivo = './instancias.csv'
    columnas=['tipo', 'dias', 'trabajadores', 'demanda_dias']

    with open(nombre_archivo, 'w', newline='') as archivo:
        writer = csv.writer(archivo)
        writer.writerow(columnas)
        writer.writerows(data)

    #Mensaje de confirmación
    print(f"El archivo CSV '{nombre_archivo}' ha sido creado exitosamente.")

if __name__ == '__main__':
    main()
