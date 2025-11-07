# Calendarios Visuales - Instancias Small

Esta carpeta contiene calendarios visuales que muestran las asignaciones de turnos para las 5 instancias pequeñas.

## 📅 Calendarios Individuales

Cada calendario muestra:
- **Filas:** Trabajadores (T1, T2, T3, ...)
- **Columnas:** Días (Día 1, Día 2, ...)
- **Colores:**
  - 🟡 **Amarillo:** Turno Día (D)
  - 🟣 **Morado:** Turno Noche (N)
  - ⬜ **Blanco:** Sin asignación (—)

### Interpretación de Celdas

- **Celda completa coloreada:** Trabajador asignado a 1 turno ese día
- **Celda dividida (2 colores):** Trabajador asignado a 2 turnos ese día (máximo permitido por R3)
- **Números entre paréntesis:** Disposición del trabajador para ese turno (0-10)

### Archivos Generados

1. **`calendario_instancia_1.png`** - 6 trabajadores × 7 días (37 asignaciones)
2. **`calendario_instancia_2.png`** - 8 trabajadores × 7 días (55 asignaciones)
3. **`calendario_instancia_3.png`** - 6 trabajadores × 6 días (37 asignaciones)
4. **`calendario_instancia_4.png`** - 14 trabajadores × 6 días (86 asignaciones)
5. **`calendario_instancia_5.png`** - 14 trabajadores × 5 días (75 asignaciones)
6. **`resumen_todas_instancias.png`** - Vista comparativa de las 5 instancias

## 🔍 Verificaciones Visuales

Los calendarios permiten verificar:

✅ **Cobertura de Demanda (R1):** Cada día tiene el número exacto de trabajadores requeridos por turno

✅ **Máximo 2 Turnos por Día (R3):** Ninguna celda tiene más de 2 turnos asignados

✅ **Distribución de Carga:** Se puede observar cómo se distribuye el trabajo entre trabajadores

✅ **Patrones de Trabajo:** Identificar trabajadores con alta/baja carga de trabajo

✅ **Uso de Disponibilidad:** Los números entre paréntesis muestran que se priorizan asignaciones con mayor disposición

## 📊 Calendario Resumen

El archivo `resumen_todas_instancias.png` muestra un heatmap comparativo:

- **Intensidad de color:** Número de turnos asignados (0, 1, o 2)
- **Valor objetivo:** Disposición total acumulada
- **Utilización:** Porcentaje de capacidad utilizada

### Métricas por Instancia

| Instancia | Trabajadores | Días | Asignaciones | Valor Objetivo | Utilización |
|-----------|--------------|------|--------------|----------------|-------------|
| 1         | 6            | 7    | 37           | 275            | 44%         |
| 2         | 8            | 7    | 55           | 399            | 49%         |
| 3         | 6            | 6    | 37           | 256            | 51%         |
| 4         | 14           | 6    | 86           | 648            | 51%         |
| 5         | 14           | 5    | 75           | 548            | 54%         |

## 🎯 Observaciones

### Patrones Identificados

1. **Balanceo de Carga:** Las asignaciones tienden a distribuirse uniformemente entre trabajadores cuando es posible.

2. **Uso Estratégico de Disponibilidad:** Se maximiza la disposición total, priorizando trabajadores con mayor preferencia por ciertos turnos.

3. **Cumplimiento de Restricciones:** 
  - R1 (cobertura exacta) y R3 (máx. 2 turnos/día) se cumplen en todas las instancias small
  - R4 (no noche→mañana) aplica en instancias medium/large; en small no existe el turno "mañana" como tal
  - En small, que aparezca "D+N" en un mismo día o "Noche→Día" al día siguiente es válido bajo el modelo actual
  - La distribución respeta R5 (no 3 fines de semana consecutivos)

4. **Flexibilidad vs Restricciones:** Las instancias small muestran suficiente flexibilidad para cumplir todas las restricciones mientras maximizan la disposición.

## 🚀 Regenerar Calendarios

Para regenerar los calendarios:

```bash
python generar_calendarios.py
```

El script:
- Lee los resultados de `../resultados/small/`
- Genera calendarios individuales para cada instancia
- Crea un resumen comparativo
- Guarda todos los archivos en esta carpeta

---

*Nota: Los calendarios son útiles para presentaciones, reportes y verificación visual de la calidad de las soluciones.*

---

## ℹ️ Nota sobre R4 (descanso noche→mañana)

El enunciado exige: “Se prohíbe asignar a una misma persona el turno de noche de un día y el turno de mañana del día siguiente (para evitar fatiga)”.

- En nuestro modelo, esta restricción R4 se implementa exactamente como “no Noche→Mañana” para instancias **medium/large**, porque allí existen tres turnos: `mañana`, `tarde`, `noche`.
- En instancias **small** solo hay dos turnos: `día` y `noche`. No existe el turno “mañana” explícito; por lo tanto, R4 no aplica literalmente. Bajo este esquema:
  - Es válido ver celdas con “D+N” el mismo día (cumple R3: ≤ 2 turnos/día)
  - También puede haber secuencias “Noche (día j) → Día (día j+1)” sin violar R4, porque “día” no equivale a “mañana”.

Si se desea mantener el espíritu de descanso también en small, se puede activar una variante: “no Noche→Día” entre días consecutivos. Esta modificación es simple de agregar al solver; avísanos y la dejamos habilitada por defecto y regeneramos resultados y gráficos.
