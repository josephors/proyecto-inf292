"""analizar_infactibilidad.py
=================================
Analiza en detalle las instancias marcadas como infactibles y produce
diagnósticos cuantitativos vinculados explícitamente a las restricciones
del modelo (R1-R7). El objetivo es justificar la infactibilidad con
indicadores medibles.

Resumen de restricciones consideradas:
    R2: Disponibilidad por turno y global (slots con disposición > 0).
    R3: Capacidad máxima diaria (≤ 2 turnos por trabajador por día).
    R4: Conflictos entre turnos noche de un día y mañana del siguiente.
    R5: No trabajar tres fines de semana consecutivos (heurística sobre demanda acumulada).
    R5.1: Activación de fines de semana (variable binaria y_{i,k}).
    R6: Límite total de carga L_i por trabajador.
    R7: Naturaleza binaria (no genera infactibilidad directa, sólo se documenta).

Entradas:
    - Archivos JSON de instancias en ../../Entrega 1/generador/instancias/large/instancia_<id>.json
        con llaves: trabajadores, dias, demanda_dias, disposicion, (opcional) max_carga_trabajador.

Salidas:
    - Carpeta ./diagnosticos/ con archivos:
            diagnostico_infactibilidad_<id>.json
        Cada JSON contiene métricas numéricas y lista de causas_identificadas.
    - Impresiones en consola con secciones numeradas de análisis.

Métricas principales calculadas:
    - demanda_total, demanda_por_turno, capacidad_maxima_R3, porcentaje_disponible (R2),
        ratio_conflictos_R4, carga_min_requerida vs L_i (R6), tensión fines de semana (R5).

Suposición para L_i (si no aparece en el JSON de instancia): L_i = floor(2H/3), donde H = número de días.

Limitaciones:
    - Heurística de R5: se aproxima necesidad de activaciones usando demanda total por fin de semana / 4.
    - No se construye un modelo exacto para y_{i,k}; se evalúa tensión agregada.
"""

import json
import math
import pandas as pd
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("ANALISIS DE INSTANCIAS INFACTIBLES")
print("=" * 80)

# Instancias infactibles identificadas
instancias_infactibles = [12, 15]

# Directorio de salida para diagnósticos (creado relativo a este script)
SCRIPT_DIR = Path(__file__).parent
DIAGNOSTICOS_DIR = SCRIPT_DIR / "diagnosticos"
DIAGNOSTICOS_DIR.mkdir(parents=True, exist_ok=True)

# ===================== Utilidades nuevas =====================

def obtener_fines_de_semana(demanda_dias):
    """Identifica pares (sábado, domingo) que conforman cada fin de semana.
    Devuelve lista de tuplas (sabado, domingo)."""
    dias = sorted(demanda_dias.keys())
    fines = []
    sabado_actual = None
    for nombre in dias:
        ln = nombre.lower()
        if "sabado" in ln or "sábado" in ln:
            sabado_actual = nombre
        elif "domingo" in ln and sabado_actual:
            fines.append((sabado_actual, nombre))
            sabado_actual = None
    return fines

def calcular_Li(datos_instancia):
    """Obtiene L_i usado en la restricción R6.
    Prioridad: si la instancia define 'max_carga_trabajador', usarlo.
    Si no, aplicar fórmula L_i = floor(2H/3) (H = días)."""
    if 'max_carga_trabajador' in datos_instancia:
        return int(datos_instancia['max_carga_trabajador'])
    H = int(datos_instancia['dias'])
    return (2 * H) // 3

def analizar_instancia(id_instancia):
    """Analiza en detalle una instancia para identificar causas de infactibilidad
    con métricas ligadas a cada restricción relevante (R2–R6)."""
    
    # Cargar instancia
    tipo = "large"
    ruta = f"../../Entrega 1/generador/instancias/{tipo}/instancia_{id_instancia}.json"
    
    with open(ruta, 'r') as f:
        datos = json.load(f)
    
    print(f"\n{'=' * 80}")
    print(f"INSTANCIA {id_instancia}")
    print(f"{'=' * 80}")
    
    num_trabajadores = datos['trabajadores']
    num_dias = datos['dias']
    
    print(f"\nCaracterísticas:")
    print(f"  - Trabajadores (|T|): {num_trabajadores}")
    print(f"  - Días (H): {num_dias}")
    print(f"  - Turnos por día (|S|): 3 (mañana, tarde, noche)")
    L_i = calcular_Li(datos)
    print(f"  - Límite de carga L_i (R6): {L_i}")
    
    # Analizar demanda total
    demanda_total_por_dia = {}
    demanda_por_turno = defaultdict(int)
    
    dias_ordenados = sorted(datos['demanda_dias'].keys())
    
    for nombre_dia in dias_ordenados:
        dia_data = datos['demanda_dias'][nombre_dia]
        total_dia = dia_data['manana'] + dia_data['tarde'] + dia_data['noche']
        demanda_total_por_dia[nombre_dia] = total_dia
        demanda_por_turno['manana'] += dia_data['manana']
        demanda_por_turno['tarde'] += dia_data['tarde']
        demanda_por_turno['noche'] += dia_data['noche']
    
    demanda_total = sum(demanda_total_por_dia.values())
    demanda_promedio_dia = demanda_total / num_dias
    
    print(f"\n1. ANÁLISIS DE DEMANDA:")
    print(f"  - Demanda total: {demanda_total} turnos")
    print(f"  - Demanda promedio por día: {demanda_promedio_dia:.2f} turnos")
    print(f"  - Demanda por turno:")
    print(f"    • Mañana: {demanda_por_turno['manana']}")
    print(f"    • Tarde: {demanda_por_turno['tarde']}")
    print(f"    • Noche: {demanda_por_turno['noche']}")
    
    # Analizar capacidad teórica
    # Restricción R3: Máximo 2 turnos por día por trabajador
    max_turnos_trabajador_dia = 2
    capacidad_maxima_teorica = num_trabajadores * num_dias * max_turnos_trabajador_dia
    
    print(f"\n2. CAPACIDAD TEÓRICA (R3):")
    print(f"  - Capacidad máxima (solo R3): {capacidad_maxima_teorica} turnos")
    print(f"  - Utilización teórica: {(demanda_total/capacidad_maxima_teorica)*100:.1f}%")
    
    ratio_demanda_capacidad = demanda_total / capacidad_maxima_teorica
    
    if ratio_demanda_capacidad > 1.0:
        print("  ADVERTENCIA: Demanda excede capacidad máxima teórica (R3) -> infactibilidad estructural.")
    
    # Analizar disponibilidad
    disponibilidad_por_trabajador = defaultdict(int)
    disponibilidad_cero = 0
    disponibilidad_total = 0
    
    for d in datos['disposicion']:
        trabajador = d['trabajador']
        disp = d['disposicion']
        
        if disp == 0:
            disponibilidad_cero += 1
        else:
            disponibilidad_total += 1
        
        disponibilidad_por_trabajador[trabajador] += (1 if disp > 0 else 0)
    
    total_slots = num_trabajadores * num_dias * 3  # 3 turnos
    porcentaje_disponible = (disponibilidad_total / total_slots) * 100
    
    print(f"\n3. ANÁLISIS DE DISPONIBILIDAD:")
    print(f"  - Slots totales: {total_slots}")
    print(f"  - Slots disponibles (disp > 0): {disponibilidad_total}")
    print(f"  - Slots no disponibles (disp = 0): {disponibilidad_cero}")
    print(f"  - Porcentaje disponible: {porcentaje_disponible:.1f}%")
    
    capacidad_real = disponibilidad_total
    
    # Verificar restricción R2: disponibilidad
    if demanda_total > capacidad_real:
        print(f"  ADVERTENCIA (R2): Demanda ({demanda_total}) > Slots disponibles ({capacidad_real})")
        print(f"     Faltante estimado: {demanda_total - capacidad_real} slots")
    
    # Analizar disponibilidad por turno
    disponibilidad_por_turno = {'manana': 0, 'tarde': 0, 'noche': 0}
    
    for d in datos['disposicion']:
        turno = d['turno']
        if d['disposicion'] > 0:
            disponibilidad_por_turno[turno] += 1
    
    print(f"\n4. DISPONIBILIDAD POR TURNO:")
    problemas_turno = []
    for turno in ['manana', 'tarde', 'noche']:
        disp = disponibilidad_por_turno[turno]
        dem = demanda_por_turno[turno]
        print(f"  - {turno.capitalize()}: {disp} disponibles vs {dem} demandados")
        if disp < dem:
            problemas_turno.append(turno)
            print(f"    FALTANTE (R2): {dem - disp}")
    
    # Analizar trabajadores con poca disponibilidad
    trabajadores_problematicos = []
    for trabajador in range(1, num_trabajadores + 1):
        slots_disponibles = disponibilidad_por_trabajador[trabajador]
        porcentaje_trab = (slots_disponibles / (num_dias * 3)) * 100
        
        if porcentaje_trab < 30:  # Menos del 30% disponible
            trabajadores_problematicos.append((trabajador, slots_disponibles, porcentaje_trab))
    
    print(f"\n5. TRABAJADORES CON BAJA DISPONIBILIDAD (< 30%):")
    print(f"  - Cantidad: {len(trabajadores_problematicos)}")
    if len(trabajadores_problematicos) > 0:
        print(f"  - Ejemplos (primeros 5):")
        for trab, slots, porc in trabajadores_problematicos[:5]:
            print(f"    • Trabajador {trab}: {slots}/{num_dias*3} slots ({porc:.1f}%)")
    
    # Analizar restricción R4: No noche-mañana consecutiva
    # Esta restricción reduce aún más la capacidad real
    print(f"\n6. IMPACTO DE RESTRICCIÓN R4 (No Noche→Mañana):")
    print(f"  - Esta restricción elimina combinaciones válidas de asignación")
    print(f"  - Con alta demanda de noche y mañana, puede causar infactibilidad")
    
    # Calcular demanda en días consecutivos
    demanda_noche_manana = 0
    for i in range(len(dias_ordenados) - 1):
        dia_actual = datos['demanda_dias'][dias_ordenados[i]]
        dia_siguiente = datos['demanda_dias'][dias_ordenados[i+1]]
        demanda_noche_manana += min(dia_actual['noche'], dia_siguiente['manana'])
    
    print(f"  - Posibles conflictos noche→mañana (pares potencialmente restringidos): ~{demanda_noche_manana}")
    ratio_conflictos = demanda_noche_manana / demanda_por_turno['noche'] if demanda_por_turno['noche'] else 0.0
    print(f"  - Ratio conflictos / demanda noche: {ratio_conflictos:.2f}")
    conflicto_R4_severo = ratio_conflictos > 0.7
    
    # DIAGNÓSTICO FINAL
    print(f"\n{'='*80}")
    print("DIAGNÓSTICO DE INFACTIBILIDAD:")
    print(f"{'='*80}")
    
    causas = []
    
    # R2 global
    if demanda_total > capacidad_real:
        causas.append(f"(R2) Demanda total {demanda_total} excede slots disponibles {capacidad_real}")
    
    if problemas_turno:
        causas.append(f"(R2) Turnos con demanda > disponibilidad: {', '.join(problemas_turno)}")
    
    if len(trabajadores_problematicos) > num_trabajadores * 0.3:
        causas.append(f"(R2) Alta proporción de trabajadores con baja disponibilidad ({len(trabajadores_problematicos)}/{num_trabajadores})")
    
    if porcentaje_disponible < 50:
        causas.append(f"(R2) Disponibilidad general muy baja ({porcentaje_disponible:.1f}%)")

    # R6 carga mínima vs L_i
    carga_min_requerida = math.ceil(demanda_total / num_trabajadores)
    if carga_min_requerida > L_i:
        causas.append(f"(R6) Límite L_i={L_i} insuficiente; carga mínima requerida={carga_min_requerida}")

    # R5 análisis heurístico weekends
    fines = obtener_fines_de_semana(datos['demanda_dias'])
    demanda_weekends = []
    for k,(sab,dom) in enumerate(fines, start=1):
        d_sab = sum(datos['demanda_dias'][sab].values())
        d_dom = sum(datos['demanda_dias'][dom].values())
        demanda_weekends.append((k, d_sab + d_dom))
    # Heurística: si en cualquier bloque de 3 fines de semana, la suma de demandas
    # supera trabajadores * 2 (porque cada trabajador puede trabajar a lo más en 2 de esos 3 weekends)
    for i in range(len(demanda_weekends)-2):
        trio = demanda_weekends[i:i+3]
        suma_trio = sum(v for _, v in trio)
        # Capacidad weekend por trabajador: asumiendo máx 2 turnos/día * 2 días = 4
        # Para activación (y_{i,k}) solo importa si trabaja ≥1 turno. Pero la restricción de no 3 consecutivos
        # implica que un trabajador está disponible a lo más en 2 de los 3 fines.
        # Consideramos demanda agregada y capacidad agregada de activaciones = trabajadores * 2.
        min_activaciones_necesarias = sum(math.ceil(v / 4) for _, v in trio)  # demanda weekend / 4 turnos máx
        if min_activaciones_necesarias > num_trabajadores * 2:
            causas.append(f"(R5) Demanda acumulada en weekends {trio[0][0]}–{trio[-1][0]} excede capacidad de activaciones (2 de 3 consecutivos) por trabajador")
            break

    if conflicto_R4_severo:
        causas.append(f"(R4) Conflictos noche→mañana muy altos (ratio {ratio_conflictos:.2f})")
    
    if causas:
        print("\nCAUSAS IDENTIFICADAS:")
        for i, causa in enumerate(causas, 1):
            print(f"{i}. {causa}")
    else:
        print("\nNo se identificaron causas obvias. Posiblemente por:")
        print("- Combinación de restricciones R4 y R5")
        print("- Distribución específica de disponibilidad por día/turno")
        print("- Conflictos de restricciones en configuraciones específicas")
    
    diagnostico = {
        'id': id_instancia,
        'trabajadores': num_trabajadores,
        'dias': num_dias,
        'L_i': L_i,
        'carga_min_requerida': carga_min_requerida,
        'demanda_total': demanda_total,
        'capacidad_maxima_R3': capacidad_maxima_teorica,
        'capacidad_real_slots_disponibles_R2': capacidad_real,
        'porcentaje_disponible': porcentaje_disponible,
        'ratio_conflictos_R4': ratio_conflictos,
        'turnos_con_faltantes_R2': problemas_turno,
        'causas_identificadas': causas
    }
    # Guardar JSON por instancia
    out_json = DIAGNOSTICOS_DIR / f"diagnostico_infactibilidad_{id_instancia}.json"
    out_json.write_text(json.dumps(diagnostico, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"  Archivo diagnóstico guardado en {out_json}")
    return diagnostico

# Analizar ambas instancias infactibles
resultados = []
for id_inst in instancias_infactibles:
    resultado = analizar_instancia(id_inst)
    resultados.append(resultado)

# Comparación
print(f"\n\n{'='*80}")
print("COMPARACIÓN DE INSTANCIAS INFACTIBLES")
print(f"{'='*80}")

df = pd.DataFrame(resultados)
print("\n", df.to_string(index=False))

print("\nTABLA MÉTRICAS CLAVE (por instancia):")
cols_show = ["id","demanda_total","capacidad_real_slots_disponibles_R2","L_i","carga_min_requerida","ratio_conflictos_R4"]
print(df[cols_show].to_string(index=False))

print(f"\n\n{'='*80}")
print("CONCLUSIÓN GENERAL")
print(f"{'='*80}")
print("""
Las instancias 12 y 15 son INFACTIBLES principalmente debido a:

1. (R2) DESBALANCE ENTRE DEMANDA Y DISPONIBILIDAD.
    - Demanda excede slots disponibles y turnos específicos presentan faltantes.

2. (R6) LÍMITE DE CARGA L_i tensionado.
    - La carga mínima necesaria por trabajador supera (o se acerca mucho) al límite definido L_i.

3. (R4) CONFLICTOS NOCHE→MAÑANA elevados.
    - Alta proporción de demanda en turnos noche enlazada con demanda fuerte en mañanas siguientes reduce reutilización.

4. (R5) DEMANDA ACUMULADA EN FINES DE SEMANA.
    - Bloques de 3 fines de semana obligan a muchos trabajadores a estar activos casi siempre, chocando con la prohibición de 3 consecutivos.

RECOMENDACIONES PARA EVITAR INFACTIBILIDAD:
- Elevar disponibilidad promedio por encima de 60–65%.
- Garantizar para cada turno disponibilidad ≥ 1.2 × demanda.
- Aliviar la demanda en secuencias de 3 fines de semana muy cargadas.
- Ajustar L_i (aumentar) o reducir demanda agregada si carga mínima > L_i.
- Redistribuir demanda para bajar ratio conflictos noche→mañana.
""")
print("=" * 80)
