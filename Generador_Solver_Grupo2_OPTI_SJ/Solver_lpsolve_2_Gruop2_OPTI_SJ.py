#!/usr/bin/env python3
"""
Solucionador de instancias de asignación de turnos — versión lpsolve55.

Este archivo contiene una reimplementación completa del modelo original —que
utilizaba PuLP con CBC— ahora expresado directamente en términos del solver
lp_solve 5.5 a través de la interfaz `lpsolve55`.

Se conservan íntegramente las restricciones R1..R5.1 definidas en la
especificación del proyecto:

    R1: Cobertura exacta de demanda por turno
    R2: Prohibición de asignar turnos con disposición 0
    R3: Máximo de 2 turnos por día por trabajador
    R4: Prohibición de asignar turno noche seguido por turno mañana
    R5: No trabajar 3 fines de semana consecutivos
    R5.1: Enlace bidireccional entre `x` y `w` (x ≤ w, y w ≤ Σ x)

Tecnología utilizada:
    - lpsolve55: wrapper Python para lp_solve 5.5
    - Modelo formulado manualmente mediante índices columna–variable.

Nota:
    Este modelo ELIMINA explícitamente R6
    (tope global de carga). No se implementa ningún límite L_i.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from lpsolve55 import lpsolve


# ============================================================
#              UTILIDADES DE CARGA Y PREPROCESO
# ============================================================

def cargar_instancia(ruta_json):
    """
    Carga una instancia JSON desde disco.

    Args:
        ruta_json: ruta al archivo de instancia.

    Returns:
        dict con claves como 'trabajadores', 'dias', 'demanda_dias',
        'disposicion', 'tipo', etc.
    """
    with open(ruta_json, 'r', encoding='utf-8') as f:
        return json.load(f)


def obtener_turnos(tipo_instancia):
    """
    Determina el conjunto de turnos disponibles según el tipo de instancia.

    Small  -> ["dia", "noche"]
    Medium/Large -> ["manana", "tarde", "noche"]
    """
    if tipo_instancia == "small":
        return ["dia", "noche"]
    else:
        return ["manana", "tarde", "noche"]


def es_fin_de_semana(nombre_dia):
    """
    Determina si un nombre de día corresponde a sábado o domingo.

    Maneja tanto "sábado" como "sabado" (sin tilde).
    """
    nl = nombre_dia.lower()
    return "sabado" in nl or "sábado" in nl or "domingo" in nl


def obtener_fines_de_semana(datos_instancia):
    """
    Identifica fines de semana consecutivos dentro de los días definidos.

    Devuelve una lista de listas, donde cada sublista contiene los índices
    1-based de los días que componen un fin de semana.
    Ejemplo:
        → [[6,7], [13,14], ...]
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


# ============================================================
#                  MAPEO DE VARIABLES x_ijt y w_ik
# ============================================================

def crear_mapeo_indices(num_trabajadores, num_dias, num_turnos, num_fines):
    """
    Crea un mapeo explícito columna → variable para lp_solve.

    lp_solve maneja todas las variables en un vector plano 1-based.
    Por lo tanto aquí construimos dos funciones:

        index_x(i,j,t) → índice 1-based para variable x_ijt
        index_w(i,k)   → índice 1-based para variable w_ik

    El bloque de variables x va primero, seguido por todas las w.
    """
    # ---- x variables (bloque contiguo) ----
    def index_x(i, j, t):
        # Fórmula clásica para vectorizar un 3D
        return i * (num_dias * num_turnos) + j * num_turnos + t + 1

    # Offset donde comienzan las w
    offset_w = num_trabajadores * num_dias * num_turnos

    # ---- w variables ----
    def index_w(i, k):
        return offset_w + i * num_fines + k + 1

    total_vars = offset_w + num_trabajadores * num_fines

    return index_x, index_w, total_vars


# ============================================================
#          CONSTRUCCIÓN COMPLETA DEL MODELO LP_SOLVE
# ============================================================

def crear_modelo_lpsolve(datos_instancia, msg=1):
    """
    Construye y resuelve el modelo PLE mediante lp_solve.

    Se implementan R1..R5.1 exactamente como en la versión PuLP,
    pero expresadas manualmente como filas de coeficientes.

    Args:
        datos_instancia: datos crudos de la instancia cargada.
        msg: nivel de verbosidad de lp_solve.

    Returns:
        (estado, valor_objetivo, asignaciones, tiempo_resolucion)
    """

    # ----------------- Carga de datos -----------------
    num_trabajadores = datos_instancia["trabajadores"]
    num_dias = datos_instancia["dias"]
    tipo = datos_instancia["tipo"]
    turnos = obtener_turnos(tipo)
    num_turnos = len(turnos)
    turno_a_idx = {t: i for i, t in enumerate(turnos)}

    # Construcción matricial de demanda exacta (R1)
    dias_ordenados = sorted(datos_instancia["demanda_dias"].keys())
    demanda = []
    for nombre_dia in dias_ordenados:
        info = datos_instancia["demanda_dias"][nombre_dia]
        demanda.append([info.get(t, 0) for t in turnos])

    # Construcción de disposición c_ijt
    disposicion = [[[0 for _ in range(num_turnos)] for _ in range(num_dias)]
                   for _ in range(num_trabajadores)]

    for d in datos_instancia.get("disposicion", []):
        i = d["trabajador"] - 1
        j = d["dia"] - 1
        t = turno_a_idx[d["turno"]]
        disposicion[i][j][t] = d["disposicion"]

    # Identificar fines de semana (para R5 – R5.1)
    fines_de_semana = obtener_fines_de_semana(datos_instancia)
    num_fines = len(fines_de_semana)

    print("Creando modelo lpsolve:")
    print(f"  - Trabajadores: {num_trabajadores}")
    print(f"  - Días: {num_dias}")
    print(f"  - Turnos: {turnos}")
    print(f"  - Fines de semana detectados: {num_fines}")

    # ----------------- Mapeo variables -> columnas -----------------
    index_x, index_w, nvars = crear_mapeo_indices(
        num_trabajadores, num_dias, num_turnos, num_fines
    )

    # Crear modelo vacío
    lp = lpsolve('make_lp', 0, nvars)
    lpsolve('set_maxim', lp)

    try:
        lpsolve('set_verbose', lp, msg)
    except Exception:
        pass

    # ============================================================
    #                    FUNCIÓN OBJETIVO
    #      Z = Σ_i Σ_j Σ_t c_ijt * x_ijt
    # ============================================================

    obj = [0.0] * nvars
    for i in range(num_trabajadores):
        for j in range(num_dias):
            for t in range(num_turnos):
                idx = index_x(i, j, t) - 1
                obj[idx] = disposicion[i][j][t]

    # Las w no aportan a la función objetivo (0 ya por default)
    lpsolve('set_obj_fn', lp, obj)

    # ============================================================
    #                DECLARACIÓN DE VARIABLES BINARIAS
    # ============================================================

    bin_vars = []
    for i in range(num_trabajadores):
        for j in range(num_dias):
            for t in range(num_turnos):
                bin_vars.append(index_x(i, j, t))

    for i in range(num_trabajadores):
        for k in range(num_fines):
            bin_vars.append(index_w(i, k))

    lpsolve('set_binary', lp, bin_vars)

    # ============================================================
    #                       RESTRICCIONES
    # ============================================================

    def fila_cero():
        return [0.0] * nvars

    # ----------------- R1: Cobertura exacta -----------------
    count_r1 = 0
    for j in range(num_dias):
        for t in range(num_turnos):
            row = fila_cero()
            for i in range(num_trabajadores):
                row[index_x(i, j, t) - 1] = 1.0

            lpsolve('add_constraint', lp, row, '=', demanda[j][t])
            count_r1 += 1
    print(f"  - Restricciones R1 (cobertura): {count_r1}")

    # ----------------- R2: x_ijt = 0 cuando c_ijt = 0 -----------------
    count_r2 = 0
    for i in range(num_trabajadores):
        for j in range(num_dias):
            for t in range(num_turnos):
                if disposicion[i][j][t] == 0:
                    row = fila_cero()
                    row[index_x(i, j, t) - 1] = 1.0
                    lpsolve('add_constraint', lp, row, '=', 0)
                    count_r2 += 1
    print(f"  - Restricciones R2 (disponibilidad 0 → prohibición): {count_r2}")

    # ----------------- R3: Máximo 2 turnos por día -----------------
    count_r3 = 0
    for i in range(num_trabajadores):
        for j in range(num_dias):
            row = fila_cero()
            for t in range(num_turnos):
                row[index_x(i, j, t) - 1] = 1.0
            lpsolve('add_constraint', lp, row, '<=', 2)
            count_r3 += 1
    print(f"  - Restricciones R3 (máx 2 turnos/día): {count_r3}")

    # ----------------- R4: No noche -> mañana consecutiva -----------------
    count_r4 = 0
    if "noche" in turno_a_idx and "manana" in turno_a_idx:
        t_noche = turno_a_idx["noche"]
        t_man = turno_a_idx["manana"]
        for i in range(num_trabajadores):
            for j in range(num_dias - 1):
                row = fila_cero()
                row[index_x(i, j, t_noche) - 1] = 1.0
                row[index_x(i, j + 1, t_man) - 1] = 1.0
                lpsolve('add_constraint', lp, row, '<=', 1)
                count_r4 += 1
    print(f"  - Restricciones R4 (no noche→mañana): {count_r4}")

    # ----------------- R5 + R5.1: Fines de semana y variables w -----------------
    count_r5_links = 0
    count_r5_main = 0

    if num_fines >= 1:

        # ---- Enlace x ≤ w (para cada turno del fin) ----
        for i in range(num_trabajadores):
            for k, dias_fin in enumerate(fines_de_semana):
                for dia_idx in dias_fin:
                    j = dia_idx - 1
                    for t in range(num_turnos):
                        row = fila_cero()
                        row[index_x(i, j, t) - 1] = 1.0
                        row[index_w(i, k) - 1] = -1.0
                        lpsolve('add_constraint', lp, row, '<=', 0)
                        count_r5_links += 1

                # ---- Enlace w ≤ Σ x  ----
                row = fila_cero()
                row[index_w(i, k) - 1] = 1.0
                for dia_idx in dias_fin:
                    j = dia_idx - 1
                    for t in range(num_turnos):
                        row[index_x(i, j, t) - 1] -= 1.0
                lpsolve('add_constraint', lp, row, '<=', 0)
                count_r5_links += 1

        # ---- R5 principal: No 3 fines de semana consecutivos ----
        if num_fines >= 3:
            for i in range(num_trabajadores):
                for k in range(num_fines - 2):
                    row = fila_cero()
                    row[index_w(i, k) - 1] = 1.0
                    row[index_w(i, k + 1) - 1] = 1.0
                    row[index_w(i, k + 2) - 1] = 1.0
                    lpsolve('add_constraint', lp, row, '<=', 2)
                    count_r5_main += 1

    print(f"  - Restricciones R5 (enlaces y no 3 fines seguidos): links={count_r5_links}, principales={count_r5_main}")

    # ============================================================
    #                     RESOLUCIÓN DEL MODELO
    # ============================================================

    inicio = datetime.now()
    status = lpsolve('solve', lp)
    fin = datetime.now()
    tiempo_resolucion = (fin - inicio).total_seconds()

    try:
        status_code = lpsolve('get_status', lp)
    except Exception:
        status_code = status

    # Obtener objetivo y variables
    try:
        valor_objetivo = lpsolve('get_objective', lp)
    except Exception:
        valor_objetivo = None

    try:
        sol = lpsolve('get_variables', lp)[0]
    except Exception:
        sol = None

    # Interpretación de solución: extraer x_ijt = 1
    asignaciones = []
    if sol is not None:
        for i in range(num_trabajadores):
            for j in range(num_dias):
                for t in range(num_turnos):
                    if sol[index_x(i, j, t) - 1] > 0.5:
                        asignaciones.append({
                            "trabajador": i + 1,
                            "dia": j + 1,
                            "dia_nombre": dias_ordenados[j],
                            "turno": turnos[t],
                            "disposicion": disposicion[i][j][t],
                        })

    # Limpieza
    try:
        lpsolve('delete_lp', lp)
    except Exception:
        pass

    # Map de estado estándar
    estado_map = {
        0: "Optimal",
        1: "Suboptimal",
        2: "Infeasible",
        3: "Unbounded",
        4: "Degenerate",
        5: "NumericalFailure",
        6: "UserAbort",
        7: "Timeout",
        9: "Feasible",
    }
    estado = estado_map.get(status_code, f"status_{status_code}")

    return estado, valor_objetivo, asignaciones, tiempo_resolucion


# ============================================================
#       GUARDAR RESULTADOS Y PROGRAMA DE CONSOLA
# ============================================================

def guardar_resultado(datos_instancia, estado, valor_objetivo, asignaciones,
                      tiempo_resolucion, ruta_salida):
    """
    Guarda en JSON la solución obtenida, junto con metadatos de la instancia
    y métricas de optimización.
    """
    resultado = {
        "id_instancia": datos_instancia.get("id_instancia"),
        "tipo": datos_instancia.get("tipo"),
        "dias": datos_instancia.get("dias"),
        "trabajadores": datos_instancia.get("trabajadores"),
        "estado": estado,
        "valor_objetivo": valor_objetivo,
        "tiempo_resolucion_segundos": tiempo_resolucion,
        "factible": estado == "Optimal",
        "asignaciones": asignaciones,
        "fecha_resolucion": datetime.now().isoformat(),
    }

    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"\nResultado guardado en: {ruta_salida}")


def resolver_instancia(ruta_json, ruta_salida=None):
    """
    Carga una instancia desde JSON y ejecuta el solver lpsolve55.
    """
    print("=" * 70)
    print(f"Resolviendo instancia: {ruta_json}")
    print("=" * 70)

    datos = cargar_instancia(ruta_json)
    estado, obj, asignaciones, tiempo = crear_modelo_lpsolve(datos)

    if ruta_salida:
        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        guardar_resultado(datos, estado, obj, asignaciones, tiempo, ruta_salida)

    return {
        "estado": estado,
        "valor_objetivo": obj,
        "asignaciones": asignaciones,
        "tiempo": tiempo,
    }


def main():
    """
    Punto de entrada para uso como script de consola.
    """
    if len(sys.argv) < 2:
        print("Uso: python solucionador_lpsolve55.py <instancia.json> [salida.json]")
        sys.exit(1)

    ruta_json = sys.argv[1]
    ruta_salida = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(ruta_json).exists():
        print(f"Error: archivo no encontrado: {ruta_json}")
        sys.exit(1)

    resultado = resolver_instancia(ruta_json, ruta_salida)

    print("\nResumen:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
