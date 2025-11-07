# Análisis: Función Objetivo vs Tamaño de Instancia

Este análisis examina cómo se comporta el valor de la función objetivo (disposición total) en relación con el tamaño de las instancias.

## 📊 Resultados Clave

### Correlaciones con el Valor Objetivo:
- **Tamaño del problema (trabajadores × días):** 1.000 (correlación perfecta)
- **Número de trabajadores:** 0.977 (correlación muy fuerte)
- **Número de días:** 0.904 (correlación fuerte)

### Valores Promedio por Tipo:
| Tipo   | Valor Objetivo Promedio | Desv. Estándar |
|--------|-------------------------|----------------|
| Small  | 425.20                  | ±170.73        |
| Medium | 1,949.40                | ±695.55        |
| Large  | 11,143.67               | ±1,573.31      |

### Ecuación de Tendencia:
```
Valor Objetivo = 8.78 × (Trabajadores × Días) - 75.43
```

## 📈 Gráficos Generados

1. **`objetivo_vs_tamano.png`**: Gráfico de dispersión mostrando la relación lineal entre tamaño del problema y valor objetivo.

2. **`objetivo_trabajadores_dias.png`**: Subgráficos que muestran cómo el valor objetivo se relaciona individualmente con el número de trabajadores y días.

3. **`objetivo_promedio_tipo.png`**: Gráfico de barras comparando los valores objetivo promedio por tipo de instancia.

4. **`correlacion_matriz.png`**: Matriz de correlación entre todas las variables del problema.

## 🔍 Conclusiones

1. **Relación Lineal Fuerte**: Existe una correlación positiva casi perfecta entre el tamaño del problema y el valor de la función objetivo, lo que indica que el modelo escala de manera predecible.

2. **Impacto de Trabajadores > Impacto de Días**: El número de trabajadores tiene mayor influencia en el valor objetivo (0.977) que el número de días (0.904), sugiriendo que agregar más trabajadores es más efectivo para maximizar la disposición total.

3. **Escalabilidad del Modelo**: El modelo aprovecha eficientemente los recursos adicionales, manteniendo una tendencia lineal consistente en todos los tamaños de instancia.

4. **Variabilidad Creciente**: Las instancias large muestran mayor variabilidad en el valor objetivo, lo cual es esperado dado que tienen más variables de decisión y mayor espacio de soluciones.

5. **Salto Significativo**: El salto en el valor objetivo promedio de medium (1,949) a large (11,144) es aproximadamente 5.7x, mientras que de small (425) a medium es solo 4.6x, indicando un crecimiento no-lineal en el beneficio total al aumentar el tamaño.

## 🚀 Ejecución

Para regenerar los gráficos:

```bash
python generar_graficos_objetivo.py
```

## 📁 Archivos

- `generar_graficos_objetivo.py`: Script para generar todos los gráficos
- `objetivo_vs_tamano.ipynb`: Notebook interactivo con análisis completo
- `graficos/`: Carpeta con todos los gráficos generados
