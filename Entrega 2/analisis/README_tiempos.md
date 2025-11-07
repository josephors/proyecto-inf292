# Análisis: Tiempos de Resolución vs Tamaño de Instancia

Este análisis examina el comportamiento de los tiempos de resolución del solver CBC a medida que aumenta el tamaño de las instancias.

## ⏱️ Resultados Clave

### Tiempos Promedio por Tipo:
| Tipo   | Tiempo Promedio | Desv. Estándar | Min      | Max      |
|--------|----------------|----------------|----------|----------|
| Small  | 0.0122s        | ±0.0024s       | 0.0093s  | 0.0153s  |
| Medium | 0.0415s        | ±0.0136s       | 0.0258s  | 0.0624s  |
| Large  | 0.2090s        | ±0.0679s       | 0.1060s  | 0.2725s  |

### Factores de Escalamiento:
- **Medium/Small:** 3.41x
- **Large/Medium:** 5.04x
- **Large/Small:** 17.20x

### Tiempo Total de Ejecución:
**1.31 segundos** para resolver las 15 instancias

## 📈 Gráficos Generados

1. **`tiempos_vs_tamano.png`**: Tiempo de resolución vs tamaño del problema, mostrando tendencia cuadrática y diferenciando instancias factibles e infactibles.

2. **`tiempos_vs_variables.png`**: Tiempo de resolución vs número de variables de decisión.

3. **`tiempos_promedio_tipo.png`**: Gráfico de barras comparando tiempos promedio por tipo de instancia.

4. **`tiempos_comparacion_escalabilidad.png`**: 
   - Distribución de tiempos (boxplot)
   - Escalabilidad en escala log-log

## 🔍 Análisis Detallado

### Crecimiento de Tiempos

El análisis revela un **crecimiento superlineal** en los tiempos de resolución:

```
Tiempo ≈ k × (Tamaño)^α donde α ≈ 2
```

Esto es consistente con la complejidad esperada de problemas de programación lineal entera.

### Instancias Factibles vs Infactibles

| Tipo   | Estado      | Cantidad | Tiempo Promedio |
|--------|-------------|----------|-----------------|
| Small  | Factible    | 5        | 0.0122s         |
| Medium | Factible    | 5        | 0.0415s         |
| Large  | Factible    | 3        | 0.2499s         |
| Large  | Infactible  | 2        | 0.1477s         |

**Observación clave:** Las instancias infactibles se detectan ~40% más rápido que las factibles del mismo tamaño, ya que el solver puede probar la infactibilidad sin necesidad de encontrar una solución óptima.

### Eficiencia del Solver

- ✅ **Todas las instancias < 0.3s**: Excelente para aplicaciones en tiempo real
- ✅ **Small instantáneas**: ~12ms promedio
- ✅ **Medium muy rápidas**: ~42ms promedio
- ✅ **Large razonables**: ~209ms promedio

## 📊 Análisis de Escalabilidad

### Complejidad Espacial (Variables)

| Tipo   | Trabajadores | Días | Turnos | Variables Promedio |
|--------|--------------|------|--------|--------------------|
| Small  | ~9.6         | ~6.2 | 2      | ~119               |
| Medium | ~22.2        | ~10.4| 3      | ~693               |
| Large  | ~65.3        | ~20.0| 3      | ~3,837             |

**Relación Variables → Tiempo:**
- Aprox. **32x más variables** de small a large
- Resulta en **17x más tiempo** → Eficiencia sublineal respecto a variables

### Desempeño en Escala Log-Log

El gráfico log-log muestra una tendencia aproximadamente lineal con pendiente ~2, confirmando complejidad **O(n²)** donde n es el tamaño del problema.

## 🎯 Conclusiones

1. **Excelente Performance**: El solver CBC maneja eficientemente todas las instancias en tiempo práctico (< 0.3s).

2. **Escalabilidad Predecible**: El crecimiento cuadrático es esperado y manejable para los tamaños de instancia considerados.

3. **Detección Rápida de Infactibilidad**: Las instancias infactibles se detectan rápidamente sin exploración exhaustiva.

4. **Viabilidad para Producción**: Los tiempos permiten uso en aplicaciones interactivas o sistemas de planificación en tiempo real.

5. **Margen para Crecer**: Con tiempos máximos de ~0.27s, el sistema podría manejar instancias considerablemente más grandes antes de enfrentar problemas de performance.

6. **Consistencia**: Baja variabilidad dentro de cada categoría de tamaño indica comportamiento predecible del solver.

## 🚀 Ejecución

Para regenerar los gráficos:

```bash
python generar_graficos_tiempos.py
```

## 📁 Archivos

- `generar_graficos_tiempos.py`: Script para generar todos los gráficos
- `tiempos_resolucion.ipynb`: Notebook interactivo con análisis completo
- `graficos/`: Carpeta con todos los gráficos de tiempos
