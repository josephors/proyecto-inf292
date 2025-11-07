# Análisis de Resultados - Entrega 2

Este directorio contiene todos los análisis de los resultados del solver.

## 📊 Análisis Completados

### 1. ✅ Función Objetivo vs Tamaño ([README_objetivo.md](README_objetivo.md))
**Archivos:**
- `objetivo_vs_tamano.ipynb` - Notebook interactivo
- `generar_graficos_objetivo.py` - Script generador

**Hallazgos principales:**
- Correlación casi perfecta (1.000) entre tamaño y valor objetivo
- Trabajadores tienen más impacto (0.977) que días (0.904)
- Ecuación predictiva: Valor = 8.78 × Tamaño - 75.43
- Promedios: Small (425), Medium (1,949), Large (11,144)

**Gráficos:**
- `objetivo_vs_tamano.png`
- `objetivo_trabajadores_dias.png`
- `objetivo_promedio_tipo.png`
- `correlacion_matriz.png`

---

### 2. ✅ Tiempos de Resolución ([README_tiempos.md](README_tiempos.md))
**Archivos:**
- `tiempos_resolucion.ipynb` - Notebook interactivo
- `generar_graficos_tiempos.py` - Script generador

**Hallazgos principales:**
- Crecimiento cuadrático con el tamaño (O(n²))
- Todas las instancias < 0.3s (excelente eficiencia)
- Factores de escalamiento: 3.4x (S→M), 5.0x (M→L), 17.2x (S→L)
- Infactibles se detectan ~40% más rápido

**Gráficos:**
- `tiempos_vs_tamano.png`
- `tiempos_vs_variables.png`
- `tiempos_promedio_tipo.png`
- `tiempos_comparacion_escalabilidad.png`

---

### 3. ✅ Análisis de Infactibilidad ([factibilidad.md](factibilidad.md))
**Archivos:**
- `factibilidad.md` - Documento de análisis completo
- `analizar_infactibilidad.py` - Script de análisis

**Hallazgos principales:**
- Ambas instancias tienen ~90% disponibilidad general
- Causa: **Combinación estricta de restricciones** (R1 + R4)
- R1 (cobertura exacta) no permite flexibilidad
- R4 (no noche→mañana) crea ~285-323 conflictos potenciales
- Propagación de restricciones hace imposible satisfacer todas simultáneamente

---

### 4. ✅ Calendarios Visuales (instancias pequeñas)
**Archivos:**
- `generar_calendarios.py` - Script generador de calendarios
- `graficos/calendarios/` - 6 archivos PNG generados

**Calendarios creados:**
- 5 calendarios individuales (instancias 1-5)
- 1 calendario resumen comparativo

**Características:**
- Visualización tipo tabla/heatmap
- Colores: Amarillo (día), Morado (noche)
- Muestra disposición de cada asignación
- Verifica cumplimiento visual de restricciones

---

## 📁 Estructura de Archivos

```
analisis/
├── README.md                          # Este archivo
├── README_objetivo.md                 # Documentación análisis objetivo
├── README_tiempos.md                  # Documentación análisis tiempos
├── factibilidad.md                    # Análisis infactibilidad ✅
├── objetivo_vs_tamano.ipynb           # Notebook objetivo
├── tiempos_resolucion.ipynb           # Notebook tiempos
├── generar_graficos_objetivo.py       # Script generador objetivo
├── generar_graficos_tiempos.py        # Script generador tiempos
├── analizar_infactibilidad.py         # Script análisis infactibilidad ✅
└── graficos/
    ├── objetivo_vs_tamano.png
    ├── objetivo_trabajadores_dias.png
    ├── objetivo_promedio_tipo.png
    ├── correlacion_matriz.png
    ├── tiempos_vs_tamano.png
    ├── tiempos_vs_variables.png
    ├── tiempos_promedio_tipo.png
    ├── tiempos_comparacion_escalabilidad.png
    └── calendarios/                   # ✅ Completado
        ├── README.md
        ├── calendario_instancia_1.png
        ├── calendario_instancia_2.png
        ├── calendario_instancia_3.png
        ├── calendario_instancia_4.png
        ├── calendario_instancia_5.png
        └── resumen_todas_instancias.png
```

## 🚀 Ejecución Rápida

Para regenerar todos los gráficos:

```bash
# Análisis de función objetivo
python generar_graficos_objetivo.py

# Análisis de tiempos
python generar_graficos_tiempos.py
```

## 📈 Resumen de Resultados

### Instancias Procesadas
- **Total:** 15 instancias
- **Factibles:** 13 (86.7%)
- **Infactibles:** 2 (13.3%) - Instancias 12 y 15 (large)

### Performance del Solver
- **Tiempo total:** 1.31 segundos
- **Tiempo promedio:** 0.087s por instancia
- **Tiempo máximo:** 0.27s (instancia large factible)

### Calidad de Soluciones
- **Todas las factibles:** Estado "Optimal"
- **Valor objetivo promedio:** 
  - Small: 425 puntos
  - Medium: 1,949 puntos  
  - Large: 11,144 puntos

## 🎯 Conclusiones Generales

1. **Solver Altamente Eficiente:** CBC resuelve todas las instancias en tiempo práctico.

2. **Escalabilidad Predecible:** Tanto el valor objetivo como los tiempos escalan de manera predecible con el tamaño.

3. **Modelo Robusto:** El 86.7% de factibilidad indica un buen equilibrio en la generación de instancias.

4. **Listo para Producción:** Los tiempos de resolución permiten uso en aplicaciones en tiempo real.
