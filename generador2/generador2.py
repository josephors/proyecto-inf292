import random, csv

def generar_instancias():
    filas_generador=[["id_instancia", "tipo", "dias", "trabajadores", "turnos"]]
    filas_demanda= [["id", "tipo", "dias", "trabajadores", "turno", "demanda"]]
    filas_disposicion= [["id", "tipo", "dias", "trabajadores", "trabajador", "dia", "turno", "disposicion"]]
    instancias_arr= ["peq", "med", "gra"]
    dias_arr= [(5, 7), (7, 14), (14, 28)]
    trabajadores_arr= [(5, 15), (15, 45), (45, 90)]
    turnos_arr= [["dia", "noche"], ["manana", "tarde", "noche"], ["manana", "tarde", "noche"]]
    id_instancia= 1
    cantidades= [5, 5, 5]  # Cantidad de instancias por tipo
    random.seed(1234)

    for tipo_idx, tipo in enumerate(instancias_arr):
        dias_range= dias_arr[tipo_idx]
        trabajadores_range= trabajadores_arr[tipo_idx]
        turnos= turnos_arr[tipo_idx]
        for _ in range(cantidades[tipo_idx]):
            dias= random.randint(*dias_range)
            trabajadores= random.randint(*trabajadores_range)
            filas_generador.append([id_instancia, tipo, dias, trabajadores, ",".join(turnos)])

            # demanda
            for d in range(1, dias + 1):
                for turno in turnos:
                    mu= (trabajadores/len(turnos)) * random.uniform(1.0, 1.2)
                    sigma= mu*0.2
                    demanda_turno= max(0, int(random.normalvariate(mu, sigma)))
                    filas_demanda.append([id_instancia, tipo, dias, trabajadores, turno, demanda_turno])

            # disposcion
            for w in range(1, trabajadores + 1):
                for d in range(1, dias + 1):
                    for turno in turnos:
                        dispo= random.randint(0, 10)
                        filas_disposicion.append([id_instancia, tipo, dias, trabajadores, w, d, turno, dispo])

            id_instancia += 1

    return filas_demanda, filas_disposicion, filas_generador


def main():
    filas_demanda, filas_disposicion, filas_generador = generar_instancias()

    # csv de demanda
    with open('instancias_demanda.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(filas_demanda)

    # csv de disposición
    with open('instancias_disposicion.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(filas_disposicion)

    # csv de generador
    with open('instancias_generador.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(filas_generador)

if __name__ == '__main__':
    main()
