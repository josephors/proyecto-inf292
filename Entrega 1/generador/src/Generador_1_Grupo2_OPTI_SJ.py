import os
import random
import json
import csv
import shutil
from collections import defaultdict
import math

# --------------------------------------------
# Crea las carpetas necesarias para guardar las instancias generadas.
# Si ya existen, las elimina completamente para evitar duplicados o residuos de ejecuciones anteriores.
# Esto garantiza que cada ejecución comience con un entorno limpio.
# Se crean tres subcarpetas: small, medium y large, según el tipo de instancia.
# --------------------------------------------
def crear_directorios():
    for carpeta in ['../instancias/small', '../instancias/medium', '../instancias/large']:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)  # Elimina la carpeta y todo su contenido previo
        os.makedirs(carpeta, exist_ok=True)  # Crea la carpeta vacía si no existe


# --------------------------------------------
# Esta función se usa cuando, en una instancia generada, la demanda total de turnos en un día
# supera la capacidad máxima que el equipo puede cubrir (por ejemplo, más de 2 turnos por trabajador).
# En vez de eliminar turnos o repartirlos arbitrariamente, lo que hace es ajustar los valores
# proporcionalmente: reduce cada turno manteniendo su proporción original, hasta que la suma total
# se ajusta al límite permitido (target_sum).
# Esto permite mantener la estructura de la demanda sin violar la restricción R3 del modelo.
# --------------------------------------------
def scale_day(demands_dict, target_sum):
    if target_sum < 0:
        target_sum = 0  # No se permite capacidad negativa

    current_sum = sum(demands_dict.values())  # Suma actual de demandas

    if current_sum == 0:
        # Si no hay demanda, se asigna cero a todos los turnos
        for k in demands_dict:
            demands_dict[k] = 0
        return demands_dict

    # Calcula el factor de escalado proporcional
    factor = target_sum / current_sum

    scaled = {}     # Diccionario con los valores escalados
    residues = []   # Lista para guardar residuos decimales y valores originales

    for k, v in demands_dict.items():
        raw = v * factor             # Valor escalado en decimal
        flo = math.floor(raw)        # Parte entera del valor escalado
        scaled[k] = flo              # Asigna la parte entera
        residues.append((k, raw - flo, v))  # Guarda el residuo decimal y el valor original

    # Calcula cuántas unidades faltan para alcanzar el target_sum
    deficit = target_sum - sum(scaled.values())

    # Ordena los residuos por mayor parte decimal y mayor valor original
    # Esto permite distribuir los turnos restantes de forma justa
    residues.sort(key=lambda x: (x[1], x[2]), reverse=True)

    # Distribuye las unidades faltantes a los turnos con mayor residuo
    for i in range(deficit):
        if i < len(residues):
            scaled[residues[i][0]] += 1

    return scaled  # Retorna el diccionario ajustado



# --------------------------------------------
# Generador principal de instancias.
# Controla la capacidad diaria y la disponibilidad efectiva.
# Parámetros:
# - max_turnos_dia: máximo de turnos por trabajador por día (R3)
# - dispo_umbral: umbral mínimo de disposición para considerar a un trabajador disponible
# - semilla: valor opcional para reproducibilidad
# --------------------------------------------
def generar_instancias(max_turnos_dia=2, dispo_umbral=0, semilla=None):
    if semilla is not None:
        random.seed(semilla)  # Semilla fija para reproducibilidad
    else:
        random.seed()         # Semilla aleatoria por defecto

    semana_dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

    # Configuración por tipo de instancia
    tipos = ["small", "medium", "large"]
    dias_rangos = [(5, 7), (7, 14), (14, 28)]
    trabajadores_rangos = [(5, 15), (15, 45), (45, 90)]
    turnos_rangos = [["dia", "noche"], ["manana", "tarde", "noche"], ["manana", "tarde", "noche"]]

    id_instancia = 1

    for tipo, dias_rng, trab_rng, turnos in zip(tipos, dias_rangos, trabajadores_rangos, turnos_rangos):
        for i in range(5):  # Genera 5 instancias por tipo
            dias = random.randint(*dias_rng)
            trabajadores = random.randint(*trab_rng)
            cantidad_turnos = len(turnos)

            # 1) Generar disposición primero
            # Para cada trabajador, día y turno, se asigna un nivel de disposición aleatorio entre 0 y 10.
            # Esto representa la preferencia o disponibilidad del trabajador para ese turno.
            disposicion = []
            for w in range(1, trabajadores + 1):
                for d in range(1, dias + 1):
                    for turno in turnos:
                        dispo = random.randint(0, 10)  # U{0,10}
                        disposicion.append({
                            "trabajador": w,
                            "dia": d,
                            "turno": turno,
                            "disposicion": dispo
                        })

            # 2) Calcular capacidad disponible por (día, turno)
            # Se cuenta cuántos trabajadores tienen disposición positiva (> dispo_umbral) para cada combinación (día, turno).
            # Esto se usa para limitar la demanda generada más adelante (control de R1).
            avail_map = defaultdict(int)
            for fila in disposicion:
                if fila["disposicion"] > dispo_umbral:
                    avail_map[(fila["dia"], fila["turno"])] += 1

            # 3) Generar demanda respetando capacidad por turno y por día
            # Para cada día, se genera una demanda por turno usando una distribución normal truncada en cero.
            # Luego se ajusta por disponibilidad (R1) y capacidad diaria (R3), y se escala si es necesario.
            # También se respeta indirectamente R6 al limitar la carga total generada.
            demanda_dias = {}
            capacidad_dia = max_turnos_dia * trabajadores  # Capacidad total diaria (R3)
            indicador = 0  # Para numerar semanas (lunes_1, martes_1, etc.)

            for j in range(dias):
                semana_dia = semana_dias[j % 7]
                if j % 7 == 0:
                    indicador += 1
                nombre_dia = f"{semana_dia}_{indicador}"

                demandas_turnos = {}
                for turno in turnos:
                    # Media de la demanda esperada para este turno, con leve variación aleatoria
                    mu = (trabajadores / cantidad_turnos) * random.uniform(1.0, 1.2)
                    sigma = mu * 0.2
                    propuesta = max(0, int(random.normalvariate(mu, sigma)))  # Truncado en cero

                    # Limitar la demanda por la disponibilidad efectiva (R1)
                    disp_turno = avail_map.get((j + 1, turno), 0)
                    demanda_final = min(propuesta, disp_turno)
                    demandas_turnos[turno] = demanda_final

                # Si la suma de demandas del día supera la capacidad diaria, se escala proporcionalmente (R3)
                suma_dia = sum(demandas_turnos.values())
                if suma_dia > capacidad_dia:
                    demandas_turnos = scale_day(demandas_turnos, capacidad_dia)

                demanda_dias[nombre_dia] = demandas_turnos

            # 4) Guardar instancia en .json y .csv
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

# --------------------------------------------
# Ejecución principal del script
# --------------------------------------------
if __name__ == '__main__':
    crear_directorios()
    generar_instancias(max_turnos_dia=2, dispo_umbral=0, semilla=42)  # Semilla fija para reproducibilidad
    # generar_instancias(max_turnos_dia=2, dispo_umbral=0)            # Alternativa aleatoria (comentada)

    print("Instancias generadas en ../instancias/ con control de capacidad diaria y por turno.")

# --------------------------------------------
# Nota:
# Las verificaciones automáticas de factibilidad (Check A, B, C)
# se realizan en el script separado 'chequeo_factibilidad.py'.
# Allí se controla que la demanda no exceda la disponibilidad (R1),
# la capacidad diaria (R3) y la carga agregada en fines de semana (R5).
# Este script complementario puede consultarse en el repositorio indicado en el informe.
# --------------------------------------------
