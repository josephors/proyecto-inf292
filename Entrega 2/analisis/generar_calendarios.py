"""
generar_calendarios.py
---------------------------------
Genera calendarios visuales para las instancias SMALL (2 turnos: día/noche),
utilizando los resultados JSON producidos por el solver.

Entradas esperadas (JSON por instancia):
- ../resultados/small/resultado_instancia_<id>.json con claves:
    {
        "factible", "trabajadores", "dias", "valor_objetivo", "asignaciones": [
                {"trabajador", "dia", "dia_nombre", "turno" ∈ {"dia","noche"}, "disposicion"}
        ]
    }

Salidas (PNG en ./graficos/calendarios/):
- calendario_instancia_<id>.png: calendario detallado por trabajador/día.
- resumen_todas_instancias.png: heatmap compacto para instancias 1–5.

Convenciones visuales:
- Amarillo = turno día (D); Morado = turno noche (N); blanco = sin asignación.
- Celdas divididas indican dos turnos en el mismo día (máximo permitido por R3).
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

print("=" * 80)
print("GENERACIÓN DE CALENDARIOS VISUALES - INSTANCIAS SMALL")
print("=" * 80)

# Colores para los turnos
COLORES_TURNOS = {
    'dia': '#FFD93D',      # Amarillo (día)
    'noche': '#6C5CE7'     # Morado (noche)
}

def generar_calendario(id_instancia):
    """Genera un calendario visual para una instancia SMALL.

    Parámetros
    ----------
    id_instancia : int
        Identificador de la instancia (1..5) para small.

    Efectos
    -------
    Guarda un archivo PNG en graficos/calendarios/calendario_instancia_<id>.png
    con la grilla Trabajador×Día y codificación de colores por turno.
    """
    # Cargar resultado
    ruta = f'../resultados/small/resultado_instancia_{id_instancia}.json'
    
    with open(ruta, 'r') as f:
        resultado = json.load(f)
    
    if not resultado['factible']:
        print(f"  ⚠️  Instancia {id_instancia} es infactible, saltando...")
        return
    
    print(f"\n{'='*80}")
    print(f"Instancia {id_instancia}")
    print(f"{'='*80}")
    
    num_trabajadores = resultado['trabajadores']
    num_dias = resultado['dias']
    valor_objetivo = resultado['valor_objetivo']
    
    print(f"  - Trabajadores: {num_trabajadores}")
    print(f"  - Días: {num_dias}")
    print(f"  - Valor objetivo: {valor_objetivo}")
    print(f"  - Asignaciones: {len(resultado['asignaciones'])}")
    
    # Crear matriz de asignaciones
    # Matriz[trabajador][dia] = lista de turnos
    asignaciones_matriz = [[[] for _ in range(num_dias)] for _ in range(num_trabajadores)]
    
    # Obtener nombres de días únicos
    dias_info = {}
    for asig in resultado['asignaciones']:
        dia_idx = asig['dia'] - 1  # 0-indexed
        dias_info[dia_idx] = asig['dia_nombre']
    
    # Ordenar días para que empiecen en lunes
    orden_dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    
    def obtener_orden_dia(nombre_dia):
        """Retorna el índice de orden del día (0=lunes, 6=domingo)"""
        nombre_lower = nombre_dia.lower()
        for idx, dia in enumerate(orden_dias):
            if dia in nombre_lower:
                return idx
        return 999  # Por si acaso no encuentra
    
    # Ordenar días según el calendario semanal
    dias_ordenados_indices = sorted(dias_info.keys(), 
                                   key=lambda idx: obtener_orden_dia(dias_info[idx]))
    
    # Crear mapeo de índice original -> índice visual
    mapeo_visual = {idx_original: idx_visual 
                    for idx_visual, idx_original in enumerate(dias_ordenados_indices)}
    
    dias_ordenados = [dias_info[i] for i in dias_ordenados_indices]
    
    # Llenar matriz (usando el mapeo visual)
    for asig in resultado['asignaciones']:
        trabajador_idx = asig['trabajador'] - 1
        dia_idx = asig['dia'] - 1
        dia_visual = mapeo_visual[dia_idx]  # Usar posición visual
        turno = asig['turno']
        disposicion = asig['disposicion']
        
        asignaciones_matriz[trabajador_idx][dia_visual].append({
            'turno': turno,
            'disposicion': disposicion
        })
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(max(14, num_dias * 1.5), max(8, num_trabajadores * 0.8)))
    
    # Configurar ejes
    ax.set_xlim(0, num_dias)
    ax.set_ylim(0, num_trabajadores)
    
    # Dibujar grid y celdas
    for i in range(num_trabajadores):
        for j in range(num_dias):
            # Dibujar borde de celda
            rect = mpatches.Rectangle((j, i), 1, 1, linewidth=1.5, 
                                      edgecolor='black', facecolor='white')
            ax.add_patch(rect)
            
            # Obtener asignaciones de esta celda
            turnos_celda = asignaciones_matriz[i][j]
            
            if len(turnos_celda) == 0:
                # Sin asignación - dejar blanco con "—"
                ax.text(j + 0.5, i + 0.5, '—', 
                       ha='center', va='center', fontsize=12, color='gray')
            elif len(turnos_celda) == 1:
                # Un turno - llenar toda la celda
                turno_info = turnos_celda[0]
                color = COLORES_TURNOS[turno_info['turno']]
                rect_fill = mpatches.Rectangle((j, i), 1, 1, 
                                               facecolor=color, alpha=0.7)
                ax.add_patch(rect_fill)
                
                # Texto del turno
                turno_label = 'D' if turno_info['turno'] == 'dia' else 'N'
                ax.text(j + 0.5, i + 0.6, turno_label, 
                       ha='center', va='center', fontsize=14, 
                       fontweight='bold', color='black')
                
                # Disposición
                ax.text(j + 0.5, i + 0.35, f"({turno_info['disposicion']})", 
                       ha='center', va='center', fontsize=8, color='black')
            
            elif len(turnos_celda) == 2:
                # Dos turnos - dividir celda verticalmente
                for k, turno_info in enumerate(turnos_celda):
                    color = COLORES_TURNOS[turno_info['turno']]
                    y_offset = 0.5 if k == 0 else 0
                    
                    rect_fill = mpatches.Rectangle((j, i + y_offset), 1, 0.5, 
                                                   facecolor=color, alpha=0.7)
                    ax.add_patch(rect_fill)
                    
                    # Texto del turno
                    turno_label = 'D' if turno_info['turno'] == 'dia' else 'N'
                    y_text = i + y_offset + 0.35 if k == 0 else i + y_offset + 0.15
                    ax.text(j + 0.5, y_text, turno_label, 
                           ha='center', va='center', fontsize=10, 
                           fontweight='bold', color='black')
                    
                    # Disposición (más pequeña)
                    y_text_disp = i + y_offset + 0.15 if k == 0 else i + y_offset + 0.35
                    ax.text(j + 0.5, y_text_disp, f"({turno_info['disposicion']})", 
                           ha='center', va='center', fontsize=7, color='black')
    
    # Etiquetas de días (en la parte superior)
    for j in range(num_dias):
        # Nombre corto del día
        nombre_dia = dias_ordenados[j].split('_')[0][:3].upper()  # Primeras 3 letras
        ax.text(j + 0.5, num_trabajadores + 0.3, nombre_dia, 
               ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Número de día
        ax.text(j + 0.5, num_trabajadores + 0.05, f"Día {j+1}", 
               ha='center', va='bottom', fontsize=8, color='gray')
    
    # Etiquetas de trabajadores (a la izquierda)
    for i in range(num_trabajadores):
        ax.text(-0.2, i + 0.5, f'Trabajador {i+1}', 
               ha='right', va='center', fontsize=11, fontweight='bold')
    
    # Título
    ax.text(num_dias / 2, num_trabajadores + 0.9, 
           f'Instancia {id_instancia} - Asignación de Turnos', 
           ha='center', va='bottom', fontsize=16, fontweight='bold')
    
    ax.text(num_dias / 2, num_trabajadores + 0.6, 
           f'Valor Objetivo: {valor_objetivo} | {num_trabajadores} Trabajadores × {num_dias} Días', 
           ha='center', va='bottom', fontsize=11, color='gray')
    
    # Leyenda
    legend_elements = [
        mpatches.Patch(facecolor=COLORES_TURNOS['dia'], alpha=0.7, 
                      edgecolor='black', label='Turno Día (D)'),
        mpatches.Patch(facecolor=COLORES_TURNOS['noche'], alpha=0.7, 
                      edgecolor='black', label='Turno Noche (N)'),
        mpatches.Patch(facecolor='white', edgecolor='black', label='Sin asignación (—)')
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', 
             bbox_to_anchor=(1.02, 1), fontsize=10, frameon=True, shadow=True)
    
    # Agregar nota explicativa
    nota = "Nota: Números entre paréntesis indican la disposición del trabajador (0-10)"
    ax.text(num_dias / 2, -0.7, nota, 
           ha='center', va='top', fontsize=9, style='italic', color='gray')
    
    # Ocultar ejes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Ajustar límites
    ax.set_xlim(-0.5, num_dias + 0.5)
    ax.set_ylim(-1, num_trabajadores + 1.2)
    
    plt.tight_layout()
    
    # Guardar
    output_path = f'graficos/calendarios/calendario_instancia_{id_instancia}.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Guardado: {output_path}")
    
    plt.close()

# Generar calendarios para todas las instancias small (1-5)
for i in range(1, 6):
    try:
        generar_calendario(i)
    except Exception as e:
        print(f"  ❌ Error en instancia {i}: {e}")

print("\n" + "=" * 80)
print("CALENDARIO RESUMEN - TODAS LAS INSTANCIAS")
print("=" * 80)

# Crear un resumen visual de todas las instancias
fig, axes = plt.subplots(1, 5, figsize=(22, 8.5))
fig.subplots_adjust(left=0.14, right=0.98, top=0.92, bottom=0.28)

for idx, instancia_id in enumerate(range(1, 6)):
    ax = axes[idx]
    
    # Cargar resultado
    with open(f'../resultados/small/resultado_instancia_{instancia_id}.json', 'r') as f:
        resultado = json.load(f)
    
    num_trabajadores = resultado['trabajadores']
    num_dias = resultado['dias']
    num_asignaciones = len(resultado['asignaciones'])
    valor_objetivo = resultado['valor_objetivo']
    
    # Calcular métricas
    max_asignaciones = num_trabajadores * num_dias * 2  # Máximo 2 turnos/día
    utilizacion = (num_asignaciones / max_asignaciones) * 100
    
    # Matriz simplificada (contar turnos por celda)
    matriz = np.zeros((num_trabajadores, num_dias))
    
    for asig in resultado['asignaciones']:
        i = asig['trabajador'] - 1
        j = asig['dia'] - 1
        matriz[i][j] += 1
    
    # Heatmap
    im = ax.imshow(matriz, cmap='YlOrRd', aspect='auto', vmin=0, vmax=2)
    
    # Etiquetas
    ax.set_xticks(range(num_dias))
    ax.set_xticklabels([f'D{i+1}' for i in range(num_dias)], fontsize=8)
    ax.set_yticks(range(num_trabajadores))
    ax.set_yticklabels([f'T{i+1}' for i in range(num_trabajadores)], fontsize=9)
    
    # Título con información más descriptiva
    titulo = f'Instancia {instancia_id}\n'
    titulo += f'{num_trabajadores} trabajadores × {num_dias} días\n'
    titulo += f'Valor Obj: {valor_objetivo:.0f} | Util: {utilizacion:.0f}%'
    ax.set_title(titulo, fontsize=9, fontweight='bold', pad=10)
    
    # Agregar números en celdas
    for i in range(num_trabajadores):
        for j in range(num_dias):
            val = int(matriz[i][j])
            if val > 0:
                ax.text(j, i, str(val), ha='center', va='center', 
                       color='white' if val == 2 else 'black', 
                       fontsize=9, fontweight='bold')

# Colorbar más descriptiva
cbar = fig.colorbar(im, ax=axes, orientation='horizontal', 
                    fraction=0.08, pad=0.20, aspect=40)
cbar.set_label('Número de turnos asignados por trabajador por día', 
               fontsize=11, fontweight='bold')
cbar.set_ticks([0, 1, 2])
cbar.set_ticklabels(['0 turnos\n(descanso)', '1 turno', '2 turnos\n(máximo)'], 
                    fontsize=9)

plt.suptitle('Resumen de Asignaciones - Instancias Small', 
            fontsize=15, fontweight='bold', y=1.15, x= 0.6)

# Agregar subtítulo explicativo
fig.text(0.5, 0.06, 
         'Valor Obj = Suma de disposiciones | Util = % de slots utilizados respecto al máximo posible  | T = Trabajador Indexado (T #Num Trabajador) | D = Día Indexado (D #Num día de la semana (Lun(1)-Dom(7))',
         ha='center', fontsize=10, style='italic', color='gray')
plt.savefig('graficos/calendarios/resumen_todas_instancias.png', 
           dpi=300, bbox_inches='tight', pad_inches=1.2, facecolor='white')
print("  ✓ Guardado: graficos/calendarios/resumen_todas_instancias.png")
plt.close()

print("\n" + "=" * 80)
print("✓ Calendarios generados exitosamente!")
print("=" * 80)
print("""
Los calendarios muestran:
  - Cada celda representa un trabajador (fila) en un día (columna)
  - Color amarillo: Turno Día (D)
  - Color morado: Turno Noche (N)
  - Celdas divididas: Trabajador hace 2 turnos ese día
  - Números entre paréntesis: Disposición del trabajador (0-10)
  
Los calendarios permiten verificar visualmente:
  ✓ Cobertura de turnos
  ✓ Distribución de carga entre trabajadores
  ✓ Cumplimiento de restricciones
  ✓ Patrones de asignación
""")
print("=" * 80)
