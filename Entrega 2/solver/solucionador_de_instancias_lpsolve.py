"""
Solucionador de instancias de asignación de turnos usando PuLP.

Este script resuelve el problema de asignación de turnos a trabajadores
usando programación lineal entera con PuLP (puede usar CBC o GLPK).

Modelo:
- Función Objetivo: Maximizar Σ Σ Σ x_ijt · c_ijt
- Restricciones:
  R1: Cobertura exacta de demanda por turno
  R2: Solo asignar si hay disponibilidad > 0
  R3: Máximo 2 turnos por día por trabajador
  R4: No trabajar turno noche y luego turno mañana consecutiva
  R5: No trabajar 3 fines de semana consecutivos
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import pulp


def cargar_instancia(ruta_json):
    """Carga una instancia desde un archivo JSON."""
    with open(ruta_json, 'r', encoding='utf-8') as f:
        return json.load(f)


def obtener_turnos(tipo_instancia):
    """Retorna la lista de turnos según el tipo de instancia."""
    if tipo_instancia == "small":
        return ["dia", "noche"]
    else:  # medium y large
        return ["manana", "tarde", "noche"]


def es_fin_de_semana(nombre_dia):
    """Determina si un día es fin de semana basándose en su nombre."""
    nombre_lower = nombre_dia.lower()
    return "sabado" in nombre_lower or "domingo" in nombre_lower


def obtener_fines_de_semana(datos_instancia):
    """
    Retorna una lista de listas, donde cada sublista contiene
    los índices de días (1-indexed) que corresponden a un fin de semana.
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
    
    # Si el último día es fin de semana
    if fin_actual:
        fines_de_semana.append(fin_actual)
    
    return fines_de_semana


def crear_modelo_pulp(datos_instancia):
    """
    Crea y resuelve el modelo de programación lineal usando PuLP.
    
    Returns:
        tuple: (estado, valor_objetivo, asignaciones, tiempo_resolucion)
    """
    num_trabajadores = datos_instancia["trabajadores"]
    num_dias = datos_instancia["dias"]
    tipo = datos_instancia["tipo"]
    turnos = obtener_turnos(tipo)
    num_turnos = len(turnos)
    
    # Mapeo de turnos a índices
    turno_a_idx = {t: i for i, t in enumerate(turnos)}
    
    # Preparar demanda: demanda[j][t] = número requerido
    dias_ordenados = sorted(datos_instancia["demanda_dias"].keys())
    demanda = []
    for nombre_dia in dias_ordenados:
        dia_data = datos_instancia["demanda_dias"][nombre_dia]
        demanda_dia = [dia_data.get(t, 0) for t in turnos]
        demanda.append(demanda_dia)
    
    # Preparar disposición: disposicion[i][j][t]
    disposicion = [[[0 for _ in range(num_turnos)] for _ in range(num_dias)] 
                   for _ in range(num_trabajadores)]
    
    for d in datos_instancia["disposicion"]:
        i = d["trabajador"] - 1  # Convertir a 0-indexed
        j = d["dia"] - 1
        t_idx = turno_a_idx[d["turno"]]
        disposicion[i][j][t_idx] = d["disposicion"]
    
    # Variables auxiliares para R5 (fines de semana)
    fines_de_semana = obtener_fines_de_semana(datos_instancia)
    num_fines = len(fines_de_semana)
    
    print(f"Creando modelo LP:")
    print(f"  - Trabajadores: {num_trabajadores}")
    print(f"  - Días: {num_dias}")
    print(f"  - Turnos: {turnos}")
    print(f"  - Fines de semana: {num_fines}")
    
    # Crear modelo PuLP
    modelo = pulp.LpProblem("Asignacion_Turnos", pulp.LpMaximize)
    
    # ============== VARIABLES DE DECISIÓN ==============
    # x[i][j][t]: 1 si trabajador i trabaja día j en turno t
    x = [[[pulp.LpVariable(f"x_{i}_{j}_{t}", cat='Binary')
           for t in range(num_turnos)]
          for j in range(num_dias)]
         for i in range(num_trabajadores)]
    
    # w[i][k]: 1 si trabajador i trabaja en fin de semana k
    w = [[pulp.LpVariable(f"w_{i}_{k}", cat='Binary')
          for k in range(num_fines)]
         for i in range(num_trabajadores)]
    
    # ============== FUNCIÓN OBJETIVO ==============
    # Maximizar: Σ Σ Σ x_ijt · c_ijt
    modelo += pulp.lpSum(
        x[i][j][t] * disposicion[i][j][t]
        for i in range(num_trabajadores)
        for j in range(num_dias)
        for t in range(num_turnos)
    ), "Maximizar_Disposicion"
    
    # ============== RESTRICCIONES ==============
    
    # R1: Cobertura exacta de turnos
    # Σ_i x_ijt = r_jt  ∀j,t
    for j in range(num_dias):
        for t in range(num_turnos):
            modelo += (
                pulp.lpSum(x[i][j][t] for i in range(num_trabajadores)) == demanda[j][t],
                f"Cobertura_dia_{j}_turno_{t}"
            )
    
    print(f"  - Restricciones R1 (cobertura): {num_dias * num_turnos}")
    
    # R2: Solo asignar si hay disponibilidad
    # x_ijt <= 1_{c_ijt > 0}  ∀i,j,t
    for i in range(num_trabajadores):
        for j in range(num_dias):
            for t in range(num_turnos):
                if disposicion[i][j][t] == 0:
                    modelo += (x[i][j][t] == 0, f"Disponibilidad_{i}_{j}_{t}")
    
    print(f"  - Restricciones R2 (disponibilidad): aplicadas")
    
    # R3: Máximo 2 turnos por día
    # Σ_t x_ijt <= 2  ∀i,j
    for i in range(num_trabajadores):
        for j in range(num_dias):
            modelo += (
                pulp.lpSum(x[i][j][t] for t in range(num_turnos)) <= 2,
                f"Max2Turnos_{i}_{j}"
            )
    
    print(f"  - Restricciones R3 (max 2 turnos/día): {num_trabajadores * num_dias}")
    
    # R4: No trabajar noche y luego mañana consecutiva
    # x_i,j,noche + x_i,j+1,mañana <= 1  ∀i, ∀j<H
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
    if num_fines >= 3:
        # Vincular w_ik con trabajar en fin de semana k
        for i in range(num_trabajadores):
            for k in range(num_fines):
                dias_fin = fines_de_semana[k]
                # Si trabaja algún turno en el fin de semana k, entonces w_ik = 1
                # w_ik >= x_ijt para cualquier j en fin_k, t
                # Simplificado: M * w_ik >= Σ_{j∈fin_k} Σ_t x_ijt
                M = len(dias_fin) * num_turnos
                modelo += (
                    pulp.lpSum(x[i][j - 1][t] 
                              for dia_idx in dias_fin 
                              for j in [dia_idx]
                              for t in range(num_turnos)) <= M * w[i][k],
                    f"VincularFin_{i}_{k}"
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
    
    # ============== RESOLVER ==============
    print("\nResolviendo modelo...")
    inicio = datetime.now()
    
    # Usar el solver predeterminado (CBC)
    solver = pulp.PULP_CBC_CMD(msg=1, timeLimit=300)  # 5 minutos límite
    resultado = modelo.solve(solver)
    
    fin = datetime.now()
    tiempo_resolucion = (fin - inicio).total_seconds()
    
    # Interpretar resultado
    estado = pulp.LpStatus[resultado]
    print(f"Estado: {estado}")
    print(f"Tiempo: {tiempo_resolucion:.2f} segundos")
    
    valor_objetivo = None
    asignaciones = []
    
    if resultado == pulp.LpStatusOptimal:
        valor_objetivo = pulp.value(modelo.objective)
        print(f"Valor objetivo: {valor_objetivo}")
        
        # Extraer solución
        for i in range(num_trabajadores):
            for j in range(num_dias):
                for t in range(num_turnos):
                    if pulp.value(x[i][j][t]) > 0.5:  # Es 1
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
    """Guarda el resultado de la resolución en formato JSON."""
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
    Resuelve una instancia completa.
    
    Args:
        ruta_json: Ruta al archivo JSON de la instancia
        ruta_salida: Ruta donde guardar el resultado (opcional)
    """
    print("=" * 70)
    print(f"Resolviendo instancia: {ruta_json}")
    print("=" * 70)
    
    # Cargar instancia
    datos_instancia = cargar_instancia(ruta_json)
    
    # Resolver
    estado, valor_objetivo, asignaciones, tiempo = crear_modelo_pulp(datos_instancia)
    
    # Guardar resultado si se especifica ruta
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
    """Función principal para uso desde línea de comandos."""
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
