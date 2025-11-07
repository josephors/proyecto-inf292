"""
Solucionador de instancias de asignación de turnos.

Implementa un modelo de Programación Lineal Entera Mixta (MILP) para resolver
el problema de asignación de turnos a trabajadores, maximizando la disposición
total del personal asignado.

Tecnología: PuLP con solver CBC.

Restricciones implementadas:
  R1: Cobertura exacta de demanda por turno
  R2: Asignación solo si hay disponibilidad positiva
  R3: Máximo 2 turnos por día por trabajador
  R4: No asignar turno noche seguido de turno mañana consecutiva
  R5: No trabajar 3 fines de semana consecutivos (con enlace bidireccional)
  R6: Tope de carga total por trabajador
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import math
import pulp


def cargar_instancia(ruta_json):
    """
    Carga una instancia desde un archivo JSON.
    
    Args:
        ruta_json: Ruta al archivo JSON de la instancia.
        
    Returns:
        dict: Datos de la instancia con claves 'trabajadores', 'dias', 
              'demanda_dias', 'disposicion', etc.
    """
    with open(ruta_json, 'r', encoding='utf-8') as f:
        return json.load(f)


def obtener_turnos(tipo_instancia):
    """
    Determina el conjunto de turnos según el tipo de instancia.
    
    Args:
        tipo_instancia: 'small', 'medium' o 'large'.
        
    Returns:
        list: Lista de turnos. Small: ["dia", "noche"].
              Medium/Large: ["manana", "tarde", "noche"].
    """
    if tipo_instancia == "small":
        return ["dia", "noche"]
    else:
        return ["manana", "tarde", "noche"]


def es_fin_de_semana(nombre_dia):
    """
    Determina si un día es fin de semana.
    
    Args:
        nombre_dia: Nombre del día (e.g., "sabado_1", "domingo_2").
        
    Returns:
        bool: True si el día es sábado o domingo.
    """
    nombre_lower = nombre_dia.lower()
    return "sabado" in nombre_lower or "domingo" in nombre_lower


def obtener_fines_de_semana(datos_instancia):
    """
    Identifica los fines de semana en la instancia.
    
    Un fin de semana es una secuencia consecutiva de días (sábado-domingo)
    que se interrumpe al llegar un día laborable.
    
    Args:
        datos_instancia: Diccionario con la clave 'demanda_dias'.
        
    Returns:
        list[list[int]]: Lista de fines de semana. Cada elemento es una lista
                         con los índices de días (1-indexed) del fin de semana.
                         Ejemplo: [[6, 7], [13, 14]] para 2 fines de semana.
    """
    dias_ordenados = sorted(datos_instancia["demanda_dias"].keys())
    fines_de_semana = []
    fin_actual = []
    
    for idx, nombre_dia in enumerate(dias_ordenados, start=1):
        if es_fin_de_semana(nombre_dia):
            fin_actual.append(idx)
        else:
            if fin_actual:
                fines_de_semana.append(fin_actual)
                fin_actual = []
    
    if fin_actual:
        fines_de_semana.append(fin_actual)
    
    return fines_de_semana


def crear_modelo_pulp(datos_instancia):
    """
    Construye y resuelve el modelo MILP de asignación de turnos.
    
    El modelo maximiza la suma de disposiciones de los trabajadores asignados,
    sujeto a las restricciones R1-R6.
    
    Args:
        datos_instancia: Diccionario con datos de la instancia (trabajadores,
                        dias, demanda_dias, disposicion, tipo).
    
    Returns:
        tuple: (estado, valor_objetivo, asignaciones, tiempo_resolucion)
            - estado: 'Optimal', 'Infeasible', etc.
            - valor_objetivo: Valor de la función objetivo (float o None).
            - asignaciones: Lista de dict con asignaciones realizadas.
            - tiempo_resolucion: Tiempo en segundos (float).
    """
    num_trabajadores = datos_instancia["trabajadores"]
    num_dias = datos_instancia["dias"]
    tipo = datos_instancia["tipo"]
    turnos = obtener_turnos(tipo)
    num_turnos = len(turnos)
    
    turno_a_idx = {t: i for i, t in enumerate(turnos)}
    
    # Construir matriz de demanda: demanda[j][t] = cantidad requerida de trabajadores
    # para el día j en el turno t
    dias_ordenados = sorted(datos_instancia["demanda_dias"].keys())
    demanda = []
    for nombre_dia in dias_ordenados:
        dia_data = datos_instancia["demanda_dias"][nombre_dia]
        demanda_dia = [dia_data.get(t, 0) for t in turnos]
        demanda.append(demanda_dia)
    
    # Construir matriz de disposición: disposicion[i][j][t] = nivel de disposición
    # del trabajador i para trabajar el día j en el turno t (0-10)
    disposicion = [[[0 for _ in range(num_turnos)] for _ in range(num_dias)] 
                   for _ in range(num_trabajadores)]
    
    for d in datos_instancia["disposicion"]:
        i = d["trabajador"] - 1
        j = d["dia"] - 1
        t_idx = turno_a_idx[d["turno"]]
        disposicion[i][j][t_idx] = d["disposicion"]
    
    # Identificar fines de semana para restricción R5
    fines_de_semana = obtener_fines_de_semana(datos_instancia)
    num_fines = len(fines_de_semana)
    
    print(f"Creando modelo LP:")
    print(f"  - Trabajadores: {num_trabajadores}")
    print(f"  - Días: {num_dias}")
    print(f"  - Turnos: {turnos}")
    print(f"  - Fines de semana: {num_fines}")
    
    modelo = pulp.LpProblem("Asignacion_Turnos", pulp.LpMaximize)
    
    # ============== VARIABLES DE DECISIÓN ==============
    
    # x[i][j][t]: Variable binaria que vale 1 si el trabajador i es asignado
    #             al turno t del día j, y 0 en caso contrario.
    x = [[[pulp.LpVariable(f"x_{i}_{j}_{t}", cat='Binary')
           for t in range(num_turnos)]
          for j in range(num_dias)]
         for i in range(num_trabajadores)]
    
    # w[i][k]: Variable binaria auxiliar que vale 1 si el trabajador i trabaja
    #          al menos un turno en el fin de semana k, y 0 en caso contrario.
    w = [[pulp.LpVariable(f"w_{i}_{k}", cat='Binary')
          for k in range(num_fines)]
         for i in range(num_trabajadores)]
    
    # ============== FUNCIÓN OBJETIVO ==============
    
    # Maximizar la suma de disposiciones de los trabajadores asignados:
    # Z = Σ_i Σ_j Σ_t x_ijt · c_ijt
    modelo += pulp.lpSum(
        x[i][j][t] * disposicion[i][j][t]
        for i in range(num_trabajadores)
        for j in range(num_dias)
        for t in range(num_turnos)
    ), "Maximizar_Disposicion"
    
    # ============== RESTRICCIONES ==============
    
    # R1: Cobertura exacta de demanda por turno
    # Garantiza que se asigne exactamente la cantidad requerida de trabajadores
    # a cada turno de cada día.
    # Σ_i x_ijt = r_jt  ∀j ∈ D, ∀t ∈ T
    for j in range(num_dias):
        for t in range(num_turnos):
            modelo += (
                pulp.lpSum(x[i][j][t] for i in range(num_trabajadores)) == demanda[j][t],
                f"Cobertura_dia_{j}_turno_{t}"
            )
    
    print(f"  - Restricciones R1 (cobertura): {num_dias * num_turnos}")
    
    # R2: Asignación solo si hay disponibilidad positiva
    # Un trabajador solo puede ser asignado si su disposición es mayor a cero.
    # x_ijt = 0  si c_ijt = 0,  ∀i, j, t
    for i in range(num_trabajadores):
        for j in range(num_dias):
            for t in range(num_turnos):
                if disposicion[i][j][t] == 0:
                    modelo += (x[i][j][t] == 0, f"Disponibilidad_{i}_{j}_{t}")
    
    print(f"  - Restricciones R2 (disponibilidad): aplicadas")
    
    # R3: Máximo 2 turnos por día por trabajador
    # Limita la carga diaria de cada trabajador a un máximo de 2 turnos.
    # Σ_t x_ijt ≤ 2  ∀i ∈ I, ∀j ∈ D
    for i in range(num_trabajadores):
        for j in range(num_dias):
            modelo += (
                pulp.lpSum(x[i][j][t] for t in range(num_turnos)) <= 2,
                f"Max2Turnos_{i}_{j}"
            )
    
    print(f"  - Restricciones R3 (max 2 turnos/día): {num_trabajadores * num_dias}")
    
    # R4: No asignar turno noche seguido de turno mañana consecutiva
    # Garantiza un descanso mínimo entre el final del turno noche y el inicio
    # del turno mañana del día siguiente.
    # x_i,j,noche + x_i,j+1,mañana ≤ 1  ∀i ∈ I, ∀j < H
    # Nota: Solo aplica a instancias medium/large (que tienen turno "mañana").
    if "noche" in turnos and (tipo != "small" and "manana" in turnos):
        idx_noche = turno_a_idx["noche"]
        idx_manana = turno_a_idx["manana"]
        count_r4 = 0
        for i in range(num_trabajadores):
            for j in range(num_dias - 1):
                modelo += (
                    x[i][j][idx_noche] + x[i][j + 1][idx_manana] <= 1,
                    f"NoNocheManana_{i}_{j}"
                )
                count_r4 += 1
        print(f"  - Restricciones R4 (no noche-mañana): {count_r4}")
    
    # R5: No trabajar 3 fines de semana consecutivos
    # Limita la carga de fines de semana para garantizar descanso. Se usa un
    # enlace bidireccional para vincular w_ik con "trabajar en el fin de semana k".
    #
    # Enlace bidireccional:
    #   1) x_ijt ≤ w_ik  ∀i, ∀j ∈ Finde_k, ∀t (si trabaja, w debe ser 1)
    #   2) w_ik ≤ Σ_{j∈Finde_k} Σ_t x_ijt  ∀i, ∀k (si w es 1, debe trabajar al menos un turno)
    #
    # Restricción principal:
    #   w_ik + w_i,k+1 + w_i,k+2 ≤ 2  ∀i ∈ I, ∀k ∈ {1,...,K-2}
    if num_fines >= 3:
        for i in range(num_trabajadores):
            for k in range(num_fines):
                dias_fin = fines_de_semana[k]
                # Enlace 1: x ≤ w
                for dia_idx in dias_fin:
                    j = dia_idx - 1
                    for t in range(num_turnos):
                        modelo += (
                            x[i][j][t] <= w[i][k],
                            f"Link_x_le_w_{i}_{k}_{j}_{t}"
                        )
                # Enlace 2: w ≤ Σ x
                modelo += (
                    w[i][k] <= pulp.lpSum(
                        x[i][(dia_idx - 1)][t] for dia_idx in dias_fin for t in range(num_turnos)
                    ),
                    f"Link_w_le_sumx_{i}_{k}"
                )
        
        # Restricción de no 3 fines consecutivos
        count_r5 = 0
        for i in range(num_trabajadores):
            for k in range(num_fines - 2):
                modelo += (
                    w[i][k] + w[i][k + 1] + w[i][k + 2] <= 2,
                    f"No3Fines_{i}_{k}"
                )
                count_r5 += 1
        
        print(f"  - Restricciones R5 (fines de semana): {count_r5}")
    
    # R6: Tope de carga total por trabajador
    # Limita el número total de turnos asignados a cada trabajador durante
    # todo el horizonte de planificación.
    #
    # Σ_j Σ_t x_ijt ≤ L_i  ∀i ∈ I
    #
    # El tope L puede especificarse por instancia (clave 'max_carga_trabajador')
    # o calcularse automáticamente como: L = ceil(1.25 × demanda_promedio_por_trabajador)
    total_demanda = sum(demanda[j][t] for j in range(num_dias) for t in range(num_turnos))
    promedio_por_trabajador = total_demanda / max(1, num_trabajadores)
    tope_instancia = (
        datos_instancia.get("max_carga_trabajador")
        or datos_instancia.get("max_carga_por_trabajador")
    )
    if tope_instancia is not None:
        tope_carga = int(tope_instancia)
    else:
        tope_carga = int(math.ceil(1.25 * promedio_por_trabajador))
    
    for i in range(num_trabajadores):
        modelo += (
            pulp.lpSum(x[i][j][t] for j in range(num_dias) for t in range(num_turnos)) <= tope_carga,
            f"MaxCargaTotal_{i}"
        )
    print(f"  - Restricción R6 (tope carga total): tope={tope_carga}")

    # ============== RESOLUCIÓN ==============
    
    print("\nResolviendo modelo...")
    inicio = datetime.now()
    
    # Usar solver CBC con límite de tiempo de 5 minutos
    solver = pulp.PULP_CBC_CMD(msg=1, timeLimit=300)
    resultado = modelo.solve(solver)
    
    fin = datetime.now()
    tiempo_resolucion = (fin - inicio).total_seconds()
    
    estado = pulp.LpStatus[resultado]
    print(f"Estado: {estado}")
    print(f"Tiempo: {tiempo_resolucion:.2f} segundos")
    
    valor_objetivo = None
    asignaciones = []
    
    if resultado == pulp.LpStatusOptimal:
        valor_objetivo = pulp.value(modelo.objective)
        print(f"Valor objetivo: {valor_objetivo}")
        
        # Extraer asignaciones de la solución
        for i in range(num_trabajadores):
            for j in range(num_dias):
                for t in range(num_turnos):
                    if pulp.value(x[i][j][t]) > 0.5:
                        asignaciones.append({
                            "trabajador": i + 1,
                            "dia": j + 1,
                            "dia_nombre": dias_ordenados[j],
                            "turno": turnos[t],
                            "disposicion": disposicion[i][j][t]
                        })
    
    return estado, valor_objetivo, asignaciones, tiempo_resolucion


def guardar_resultado(datos_instancia, estado, valor_objetivo, asignaciones, 
                     tiempo_resolucion, ruta_salida):
    """
    Guarda el resultado de la resolución en formato JSON.
    
    Args:
        datos_instancia: Diccionario con datos de la instancia original.
        estado: Estado de la solución ('Optimal', 'Infeasible', etc.).
        valor_objetivo: Valor de la función objetivo (o None si no hay solución).
        asignaciones: Lista de asignaciones realizadas.
        tiempo_resolucion: Tiempo de resolución en segundos.
        ruta_salida: Ruta donde guardar el archivo JSON de resultado.
    """
    resultado = {
        "id_instancia": datos_instancia["id_instancia"],
        "tipo": datos_instancia["tipo"],
        "dias": datos_instancia["dias"],
        "trabajadores": datos_instancia["trabajadores"],
        "estado": estado,
        "valor_objetivo": valor_objetivo,
        "tiempo_resolucion_segundos": tiempo_resolucion,
        "factible": estado == "Optimal",
        "asignaciones": asignaciones,
        "fecha_resolucion": datetime.now().isoformat()
    }
    
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultado guardado en: {ruta_salida}")


def resolver_instancia(ruta_json, ruta_salida=None):
    """
    Resuelve una instancia completa de asignación de turnos.
    
    Carga la instancia, construye y resuelve el modelo, y opcionalmente
    guarda el resultado en formato JSON.
    
    Args:
        ruta_json: Ruta al archivo JSON de la instancia.
        ruta_salida: Ruta donde guardar el resultado (opcional).
        
    Returns:
        dict: Diccionario con claves 'estado', 'valor_objetivo',
              'asignaciones' y 'tiempo'.
    """
    print("=" * 70)
    print(f"Resolviendo instancia: {ruta_json}")
    print("=" * 70)
    
    datos_instancia = cargar_instancia(ruta_json)
    estado, valor_objetivo, asignaciones, tiempo = crear_modelo_pulp(datos_instancia)
    
    if ruta_salida:
        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        guardar_resultado(datos_instancia, estado, valor_objetivo, 
                         asignaciones, tiempo, ruta_salida)
    
    return {
        "estado": estado,
        "valor_objetivo": valor_objetivo,
        "asignaciones": asignaciones,
        "tiempo": tiempo
    }


def main():
    """
    Función principal para uso desde línea de comandos.
    
    Uso:
        python solucionador_de_instancias_lpsolve.py <ruta_instancia.json> [ruta_salida.json]
    """
    if len(sys.argv) < 2:
        print("Uso: python solucionador_de_instancias_lpsolve.py <ruta_instancia.json> [ruta_salida.json]")
        sys.exit(1)
    
    ruta_json = sys.argv[1]
    ruta_salida = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(ruta_json).exists():
        print(f"Error: No se encontró el archivo {ruta_json}")
        sys.exit(1)
    
    resolver_instancia(ruta_json, ruta_salida)


if __name__ == "__main__":
    main()
