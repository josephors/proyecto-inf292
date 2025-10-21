import random, csv

def generar_instancias(): #peq, med, gra
    filas=[]
    filas.append(['id_instancia', 'tipo', 'dias', 'trabajadores', 'turnos'])

    instancias_arr=["peq", "med", "gra"]
    dias_arr=["5,7", "7,14", "14,28"]
    trabajadores_arr=["5,15", "15,45", "45,90"]
    turnos_arr=["dia,noche", "manana,tarde,noche", "manana,tarde,noche"]
    filas_disposicion = []
    filas_disposicion.append(['id_instancia', 'tipo', 'dias', 'trabajadores', 'trabajador', 'dia', 'turno', 'disposicion'])
    id_instancia = 1
    semana_dias=["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    random.seed(1234)
    for ins in instancias_arr: #para cada tipo de instancia
        index=instancias_arr.index(ins)

        dias_range=dias_arr[index]
        coma_idx_dias=dias_range.index(',')
        
        trabajadores_range=trabajadores_arr[index]
        coma_idx_trabs=trabajadores_range.index(',')

        turnos=turnos_arr[index].split(',')

        i=0
        while (i<5): #5 instancias para cada tipo de instancia
            #generamos cada una de las instancias
            cantidad_turnos=len(turnos)
            dias=random.randint(int(dias_range[:coma_idx_dias]), int(dias_range[coma_idx_dias+1:]))
            trabajadores=random.randint(int(trabajadores_range[:coma_idx_trabs]), int(trabajadores_range[coma_idx_trabs+1:]))
            demanda_dias={}
            j=0
            indicador=0
            while (j<dias):
                semana_dia=semana_dias[j % 7]
                if (j% 7==0):  # cada vez que damos una vuelta a la semana...
                    indicador += 1

                # generar la demanda para cada turno
                demandas_turnos=[]
                for turno in turnos:
                    mu = (trabajadores/cantidad_turnos) * random.uniform(1.0, 1.2)
                    sigma = mu*0.2

                    demanda_turno = int(random.normalvariate(mu, sigma))
                    if demanda_turno<0:
                        demanda_turno=0
                    demandas_turnos.append([turno, demanda_turno])
            # añadimos al diccionario de días
                nombre_key=semana_dia+ "_"+str(indicador)
                demanda_dias[nombre_key] = demandas_turnos

                j+=1

            filas.append([id_instancia, ins, dias, trabajadores, demanda_dias])
            for w in range(1, trabajadores + 1):
                for d in range(1, dias + 1):
                    for turno in turnos:
                        dispo= random.randint(0, 10)
                        filas_disposicion.append([id_instancia, ins, dias, trabajadores, w, d, turno, dispo])
            id_instancia+=1
            i+=1

    return filas, filas_disposicion

def main():

    instancias, disposicion=generar_instancias()

    with open('instancias_demandas.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(instancias)

    with open('instancias_disposicion.csv', mode='w', newline='') as file:
        writer_disp = csv.writer(file)
        writer_disp.writerows(disposicion)

if __name__ == '__main__':
    main()
