# Entrega 2 — Resolución (lpsolve) + Análisis

**Solver asignado:** lpsolve

**Alcance:**
- Parte 3: Modelo resoluble en lpsolve (`.lp`) + pipeline de carga de datos.
- Parte 4: Análisis de resultados (objetivo vs tamaño, explicación de infactibilidades, calendarios gráficos para instancias pequeñas).
- Parte 5: Tiempos de resolución vs tamaño.

## Estructura sugerida

```
Entrega2/
├─ README.md
├─ solver/
│  └─ lpsolve/
│     ├─ model.lp
│     ├─ data/              # datos derivados de instancias
│     │  ├─ small/  ├─ medium/  └─ large/
│     └─ run.sh             # script que resuelve y exporta a ../../resultados/
├─ analisis/
│  ├─ objetivo_vs_tamano.ipynb
│  ├─ tiempos_resolucion.ipynb
│  ├─ factibilidad.md
│  └─ graficos/calendarios/
└─ resultados/
   ├─ small/  ├─ medium/  └─ large/
```

## Flujo de trabajo
1. Transformar instancias a formato de datos compatible con `lpsolve` (archivos `.lp` + parámetros).  
2. Ejecutar `solver/lpsolve/run.sh` para resolver por lotes.  
3. Guardar soluciones y logs en `resultados/`.  
4. Analizar en `analisis/` y generar gráficos (objetivo, tiempos, calendarios).