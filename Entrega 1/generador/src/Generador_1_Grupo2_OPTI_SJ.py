import os
import random
import json
import csv
import shutil
from collections import defaultdict
import math

# Crear carpetas y eliminar contenido previo
def crear_directorios():
    for carpeta in ['../instancias/small', '../instancias/medium', '../instancias/large']:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)  # Elimina instancias anteriores
        os.makedirs(carpeta, exist_ok=True)

# Función para escalar proporcionalmente demandas por día
def scale_day(demands_dict, target_sum):
    if target_sum < 0:
        target_sum = 0
    current_sum = sum(demands_dict.values())
    if current_sum == 0:
        for k in demands_dict:
            demands_dict[k] = 0
        return demands_dict
    factor = target_sum / current_sum
    scaled = {}
    residues = []
    for k, v in demands_dict.items():
        raw = v * factor
        flo = math.floor(raw)
        scaled[k] = flo
        residues.append((k, raw - flo, v))
    deficit = target_sum - sum(scaled.values())
    residues.sort(key=lambda x: (x[1], x[2]), reverse=True)
    for i in range(deficit):
        if i < len(residues):
            scaled[residues[i][0]] += 1
    return scaled

# Generador de instancias con control de capacidad
def generar_instancias(max_turnos_dia=2, dispo_umbral=0):
    random.seed()
    semana_dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

    tipos = ["small", "medium", "large"]
    dias_rangos = [(5, 7), (7, 14), (14, 28)]
    trabajadores_rangos = [(5, 15), (15, 45), (45, 90)]
    turnos_rangos = [["dia", "noche"], ["manana", "tarde", "noche"], ["manana", "tarde", "noche"]]

    id_instancia = 1

    for tipo, dias_rng, trab_rng, turnos in zip(tipos, dias_rangos, trabajadores_rangos, turnos_rangos):
        for i in range(5):  # 5 instancias por tipo
            dias = random.randint(*dias_rng)
            trabajadores = random.randint(*trab_rng)
            cantidad_turnos = len(turnos)

            # 1) Generar disposición primero
            disposicion = []
            for w in range(1, trabajadores + 1):
                for d in range(1, dias + 1):
                    for turno in turnos:
                        dispo = random.randint(0, 10)
                        disposicion.append({
                            "trabajador": w,
                            "dia": d,
                            "turno": turno,
                            "disposicion": dispo
                        })

            # 2) Calcular capacidad disponible por (día, turno)
            avail_map = defaultdict(int)
            for fila in disposicion:
                if fila["disposicion"] > dispo_umbral:
                    avail_map[(fila["dia"], fila["turno"])] += 1

            # 3) Generar demanda respetando capacidad por turno y por día
            demanda_dias = {}
            capacidad_dia = max_turnos_dia * trabajadores
            indicador = 0

            for j in range(dias):
                semana_dia = semana_dias[j % 7]
                if j % 7 == 0:
                    indicador += 1
                nombre_dia = f"{semana_dia}_{indicador}"

                demandas_turnos = {}
                for turno in turnos:
                    mu = (trabajadores / cantidad_turnos) * random.uniform(1.0, 1.2)
                    sigma = mu * 0.2
                    propuesta = max(0, int(random.normalvariate(mu, sigma)))
                    # Limitar por disponibilidad del turno
                    disp_turno = avail_map.get((j + 1, turno), 0)
                    demanda_final = min(propuesta, disp_turno)
                    demandas_turnos[turno] = demanda_final

                # Si la suma excede la capacidad diaria, escalar proporcionalmente
                suma_dia = sum(demandas_turnos.values())
                if suma_dia > capacidad_dia:
                    demandas_turnos = scale_day(demandas_turnos, capacidad_dia)

                demanda_dias[nombre_dia] = demandas_turnos

            # 4) Guardar instancia
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
    generar_instancias(max_turnos_dia=2, dispo_umbral=0)
    print("Instancias generadas en ../instancias/ con control de capacidad diaria y por turno.")