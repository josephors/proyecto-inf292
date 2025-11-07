# Entrega 2 — Resolución + Análisis

**Solver:** PuLP con CBC (Compatible con LPSolve)

## 📁 Estructura

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
   ├─ objetivo_vs_tamano.ipynb               # Análisis función objetivo
   ├─ tiempos_resolucion.ipynb               # Análisis tiempos
   ├─ factibilidad.md                        # Explicación infactibilidades
   └─ graficos/calendarios/                  # Visualizaciones
```

## 🚀 Uso

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

## 📊 Resultados

**Total instancias:** 15  
**Óptimas:** 13 (86.7%)  
**Infactibles:** 2 (instancias 12 y 15 - large)  
**Tiempo total:** 1.31s

| Tamaño | Instancias | Óptimas | Infactibles | Tiempo promedio |
|--------|------------|---------|-------------|-----------------|
| Small  | 5          | 5       | 0           | ~0.02s          |
| Medium | 5          | 5       | 0           | ~0.04s          |
| Large  | 5          | 3       | 2           | ~0.21s          |

## 🔧 Modelo Implementado

**Función Objetivo:** Maximizar Σᵢ Σⱼ Σₜ xᵢⱼₜ · cᵢⱼₜ

**Restricciones:**
- **R1:** Cobertura exacta de demanda por turno
- **R2:** Solo asignar si hay disponibilidad > 0
- **R3:** Máximo 2 turnos por día por trabajador
- **R4:** No trabajar turno noche seguido de mañana
- **R5:** No trabajar 3 fines de semana consecutivos