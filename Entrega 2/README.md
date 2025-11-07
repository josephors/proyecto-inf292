# Entrega 2 — Resolución + Análisis

**Solver:** PuLP con CBC (Compatible con LPSolve)

## Estructura

```
Entrega 2/
├─ solver/
│  ├─ solucionador_de_instancias_lpsolve.py  # Solver principal (lógica del modelo)
│  └─ ejecutar_solver_batch.py               # Ejecutor automático (15 instancias)
├─ resultados/
│  ├─ small/                                 # Resultados instancias pequeñas
│  ├─ medium/                                # Resultados instancias medianas
│  ├─ large/                                 # Resultados instancias grandes
│  └─ resumen_ejecucion.json                 # Estadísticas generales
└─ analisis/
   ├─ generar_graficos_objetivo.py           # Script: gráficos de objetivo
   ├─ generar_graficos_tiempos.py            # Script: gráficos de tiempos
   ├─ generar_calendarios.py                 # Script: calendarios (small)
  ├─ analizar_infactibilidad.py             # Script: análisis de infactibilidad
  ├─ graficos/                              # Visualizaciones generadas (PNG)
  └─ diagnosticos/                          # JSON con diagnósticos de infactibilidad
```

## Uso

### Resolver una instancia individual:
```bash
python solver/solucionador_de_instancias_lpsolve.py \
  "../Entrega 1/generador/instancias/small/instancia_1.json" \
  "resultados/small/resultado_instancia_1.json"
```

### Resolver todas las instancias (recomendado):
```bash
python solver/ejecutar_solver_batch.py
```

## Orden de ejecución (paso a paso)

1. **Resolver todas las instancias y generar JSON de resultados**

```bash
cd "Entrega 2/solver"
python ejecutar_solver_batch.py
```

2. **Generar todos los gráficos y análisis**

```bash
cd "Entrega 2/analisis"
python generar_graficos_objetivo.py
python generar_graficos_tiempos.py
python generar_calendarios.py
python analizar_infactibilidad.py
```

3. **Compilar el reporte LaTeX** 

El documento principal es `report/report.tex`.

**Notas:**
- Entradas: JSON en `Entrega 2/resultados/`.
- Salidas: imágenes en `Entrega 2/analisis/graficos/` y diagnósticos en `Entrega 2/analisis/diagnosticos/`.
- Para actualizar artefactos, basta con re-ejecutar los scripts de análisis (paso 2).

## Referencias

- Instancias de entrada: `Entrega 1/generador/instancias/{small,medium,large}/instancia_*.json`.
- Resultados del solver: `Entrega 2/resultados/{small,medium,large}/resultado_*.json`.
- Artefactos de análisis: `Entrega 2/analisis/graficos/` y `Entrega 2/analisis/diagnosticos/`.
- Reporte LaTeX: `report/report.tex`.