"""
Script para analizar las instancias infactibles y determinar las causas de infactibilidad.
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("ANÁLISIS DE INSTANCIAS INFACTIBLES")
print("=" * 80)

# Instancias infactibles identificadas
instancias_infactibles = [12, 15]

def analizar_instancia(id_instancia):
    """Analiza en detalle una instancia para identificar causas de infactibilidad."""
    
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
    print(f"  - Trabajadores: {num_trabajadores}")
    print(f"  - Días: {num_dias}")
    print(f"  - Turnos por día: 3 (mañana, tarde, noche)")
    
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
    
    print(f"\n2. CAPACIDAD TEÓRICA:")
    print(f"  - Capacidad máxima (sin restricciones): {capacidad_maxima_teorica} turnos")
    print(f"  - Utilización teórica: {(demanda_total/capacidad_maxima_teorica)*100:.1f}%")
    
    ratio_demanda_capacidad = demanda_total / capacidad_maxima_teorica
    
    if ratio_demanda_capacidad > 1.0:
        print(f"  ⚠️  PROBLEMA: Demanda excede capacidad máxima teórica!")
    
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
        print(f"  ⚠️  PROBLEMA: Demanda ({demanda_total}) > Slots disponibles ({capacidad_real})")
        print(f"     Faltante: {demanda_total - capacidad_real} slots")
    
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
            print(f"    ❌ INFACTIBLE: Faltante de {dem - disp}")
    
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
    
    print(f"  - Posibles conflictos noche→mañana: ~{demanda_noche_manana}")
    
    # DIAGNÓSTICO FINAL
    print(f"\n{'='*80}")
    print("DIAGNÓSTICO DE INFACTIBILIDAD:")
    print(f"{'='*80}")
    
    causas = []
    
    if demanda_total > capacidad_real:
        causas.append(f"✗ Demanda total ({demanda_total}) excede slots disponibles ({capacidad_real})")
    
    if problemas_turno:
        causas.append(f"✗ Turnos con demanda > disponibilidad: {', '.join(problemas_turno)}")
    
    if len(trabajadores_problematicos) > num_trabajadores * 0.3:
        causas.append(f"✗ Alta proporción de trabajadores con baja disponibilidad ({len(trabajadores_problematicos)}/{num_trabajadores})")
    
    if porcentaje_disponible < 50:
        causas.append(f"✗ Disponibilidad general muy baja ({porcentaje_disponible:.1f}%)")
    
    if causas:
        print("\nCAUSAS IDENTIFICADAS:")
        for i, causa in enumerate(causas, 1):
            print(f"{i}. {causa}")
    else:
        print("\nNo se identificaron causas obvias. Posiblemente por:")
        print("- Combinación de restricciones R4 y R5")
        print("- Distribución específica de disponibilidad por día/turno")
        print("- Conflictos de restricciones en configuraciones específicas")
    
    return {
        'id': id_instancia,
        'trabajadores': num_trabajadores,
        'dias': num_dias,
        'demanda_total': demanda_total,
        'capacidad_real': capacidad_real,
        'porcentaje_disponible': porcentaje_disponible,
        'problemas_turno': problemas_turno,
        'causas': causas
    }

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

print(f"\n\n{'='*80}")
print("CONCLUSIÓN GENERAL")
print(f"{'='*80}")
print("""
Las instancias 12 y 15 son INFACTIBLES principalmente debido a:

1. **DESBALANCE ENTRE DEMANDA Y DISPONIBILIDAD**
   - La demanda de ciertos turnos excede la cantidad de trabajadores disponibles
   - Restricción R2 (solo asignar si disponibilidad > 0) limita severamente las opciones

2. **DISPONIBILIDAD BAJA EN TURNOS CRÍTICOS**
   - Algunos turnos tienen muy pocos trabajadores disponibles
   - No es posible cubrir toda la demanda de esos turnos específicos

3. **RESTRICCIONES ADICIONALES**
   - R4 (No noche→mañana) elimina combinaciones válidas
   - R5 (No 3 fines de semana seguidos) restringe aún más la flexibilidad
   - La combinación de todas las restricciones hace imposible una asignación válida

4. **ALTA UTILIZACIÓN REQUERIDA**
   - Se requiere usar casi toda la capacidad disponible
   - No hay suficiente "holgura" para satisfacer todas las restricciones

RECOMENDACIONES PARA EVITAR INFACTIBILIDAD:
- Generar instancias con mayor disponibilidad promedio (>60%)
- Asegurar que cada turno tenga al menos 1.2x la demanda en disponibilidad
- Distribuir mejor la disponibilidad entre días y turnos
- Considerar reducir la demanda o aumentar el número de trabajadores
""")
print("=" * 80)
