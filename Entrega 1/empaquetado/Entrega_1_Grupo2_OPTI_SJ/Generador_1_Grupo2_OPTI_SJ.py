import os
import random
import json
import csv
import shutil

# Crear carpetas y eliminar contenido previo desde generador/src hacia generador/instancias
def crear_directorios():
    for carpeta in ['../instancias/small', '../instancias/medium', '../instancias/large']:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)  # Elimina instancias anteriores
        os.makedirs(carpeta, exist_ok=True)

# Generador de instancias con comentarios explicativos
def generar_instancias():
    random.seed(1234)
    semana_dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

    # Definición de tipos de instancia y sus rangos según el enunciado
    tipos = ["small", "medium", "large"]
    dias_rangos = [(5, 7), (7, 14), (14, 28)]  # Rango de días por tipo
    trabajadores_rangos = [(5, 15), (15, 45), (45, 90)]  # Rango de trabajadores por tipo
    turnos_rangos = [["dia", "noche"], ["manana", "tarde", "noche"], ["manana", "tarde", "noche"]]  # Turnos por tipo

    id_instancia = 1

    for tipo, dias_rng, trab_rng, turnos in zip(tipos, dias_rangos, trabajadores_rangos, turnos_rangos):
        for i in range(5):  # 5 instancias por tipo
            dias = random.randint(*dias_rng)
            trabajadores = random.randint(*trab_rng)
            cantidad_turnos = len(turnos)

            demanda_dias = {}
            disposicion = []
            indicador = 0

            for j in range(dias):
                semana_dia = semana_dias[j % 7]
                if j % 7 == 0:
                    indicador += 1
                nombre_dia = f"{semana_dia}_{indicador}"

                demandas_turnos = {}
                for turno in turnos:
                    # Generación de demanda con distribución Normal
                    # La media depende del número de trabajadores y turnos
                    mu = (trabajadores / cantidad_turnos) * random.uniform(1.0, 1.2)
                    sigma = mu * 0.2  # 20% de desviación estándar
                    demanda = max(0, int(random.normalvariate(mu, sigma)))
                    demandas_turnos[turno] = demanda
                demanda_dias[nombre_dia] = demandas_turnos

            for w in range(1, trabajadores + 1):
                for d in range(1, dias + 1):
                    for turno in turnos:
                        # Disposición generada con distribución Uniforme U(0,10)
                        # 0 significa que el trabajador no puede hacer ese turno
                        dispo = random.randint(0, 10)
                        disposicion.append({
                            "trabajador": w,
                            "dia": d,
                            "turno": turno,
                            "disposicion": dispo
                        })

            instancia = {
                "id_instancia": id_instancia,
                "tipo": tipo,
                "dias": dias,
                "trabajadores": trabajadores,
                "demanda_dias": demanda_dias,
                "disposicion": disposicion
            }

            carpeta = f"../instancias/{tipo}"
            with open(f"{carpeta}/instancia_{id_instancia}.json", "w", encoding="utf-8") as fjson:
                json.dump(instancia, fjson, ensure_ascii=False, indent=4)

            with open(f"{carpeta}/instancia_{id_instancia}.csv", "w", newline='', encoding="utf-8") as fcsv:
                writer = csv.writer(fcsv)
                writer.writerow(["trabajador", "dia", "turno", "disposicion"])
                for fila in disposicion:
                    writer.writerow([fila['trabajador'], fila['dia'], fila['turno'], fila['disposicion']])

            id_instancia += 1

# Ejecutar
if __name__ == '__main__':
    crear_directorios()
    generar_instancias()
    print("Instancias generadas en ../instancias/. Instancias anteriores fueron eliminadas.")