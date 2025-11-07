# Análisis — Scripts y salidas

Este directorio contiene scripts que consumen los JSON generados por el solver y producen artefactos de análisis (gráficos e informes auxiliares). No incluye resultados ni conclusiones; esas quedan en el reporte LaTeX.

## Scripts de Análisis

### 1. **Función Objetivo vs Tamaño** (`generar_graficos_objetivo.py`)
Analiza la relación entre el valor de la función objetivo y el tamaño de las instancias.

**Gráficos generados:**
- `graficos/objetivo_vs_tamano.png`
- `graficos/objetivo_trabajadores_dias.png`
- `graficos/objetivo_promedio_tipo.png`
- `graficos/correlacion_matriz.png`

---

### 2. **Tiempos de Resolución** (`generar_graficos_tiempos.py`)
Analiza la escalabilidad temporal del solver CBC.

**Gráficos generados:**
- `graficos/tiempos_vs_tamano.png`
- `graficos/tiempos_vs_variables.png`
- `graficos/tiempos_promedio_tipo.png`
- `graficos/tiempos_comparacion_escalabilidad.png`

---

### 3. **Calendarios Visuales** (`generar_calendarios.py`)
Genera representaciones visuales de las asignaciones para instancias small.

**Gráficos generados:**
- `graficos/calendarios/calendario_instancia_{1..5}.png`
- `graficos/calendarios/resumen_todas_instancias.png`

**Características:**
- Heatmap trabajador × día
- Colores: Amarillo (día), Morado (noche)
- Muestra disposición de cada asignación
- Permite verificar visualmente R1 y R3

---

### 4. **Análisis de Infactibilidad** (`analizar_infactibilidad.py`)
Genera diagnósticos técnicos por instancia infactible en formato JSON.
Entradas: instancias `large` (ver ruta en el script). Salidas: `diagnosticos/diagnostico_infactibilidad_*.json`.

---

## Estructura

```
analisis/
├── README.md                          # Este archivo
├── generar_graficos_objetivo.py       # Script: gráficos de objetivo
├── generar_graficos_tiempos.py        # Script: gráficos de tiempos
├── generar_calendarios.py             # Script: calendarios visuales
├── analizar_infactibilidad.py         # Script: análisis de infactibilidad
├── factibilidad.md                    # Documentación de infactibilidades
├── diagnosticos/                      # JSON con diagnósticos de infactibilidad
└── graficos/                          # Directorio de salida (PNG)
    ├── objetivo_*.png
    ├── tiempos_*.png
    ├── correlacion_matriz.png
    └── calendarios/
        ├── calendario_instancia_{1..5}.png
        └── resumen_todas_instancias.png
```

## Ejecución

Para regenerar todos los gráficos tras correr el solver:

```bash
python3 generar_graficos_objetivo.py
python3 generar_graficos_tiempos.py
python3 generar_calendarios.py
```

