# Análisis de Infactibilidad

## Resumen

De las 15 instancias generadas, **2 resultaron infactibles**:
- **Instancia 12** (large): 52 trabajadores, 17 días
- **Instancia 15** (large): 78 trabajadores, 14 días

Ambas instancias fueron detectadas como infactibles por el solver CBC en menos de 0.2 segundos.

---

## Características de las Instancias Infactibles

### Instancia 12

| Métrica | Valor |
|---------|-------|
| Trabajadores | 52 |
| Días | 17 |
| Turnos por día | 3 (mañana, tarde, noche) |
| Demanda total | 1,003 turnos |
| Slots disponibles (disp > 0) | 2,418 |
| Disponibilidad general | 91.2% |
| Utilización requerida | 56.7% |

**Demanda por turno:**
- Mañana: 353 (809 disponibles)
- Tarde: 332 (805 disponibles)
- Noche: 318 (804 disponibles)

### Instancia 15

| Métrica | Valor |
|---------|-------|
| Trabajadores | 78 |
| Días | 14 |
| Turnos por día | 3 (mañana, tarde, noche) |
| Demanda total | 1,194 turnos |
| Slots disponibles (disp > 0) | 2,952 |
| Disponibilidad general | 90.1% |
| Utilización requerida | 54.7% |

**Demanda por turno:**
- Mañana: 371 (981 disponibles)
- Tarde: 397 (983 disponibles)
- Noche: 426 (988 disponibles)

---

## Análisis de las Causas

### ¿Por qué son infactibles si hay suficiente disponibilidad?

A primera vista, ambas instancias parecen tener **disponibilidad más que suficiente**:
- 90-91% de slots disponibles
- Cada turno tiene 2-3x más slots disponibles que la demanda
- Utilización requerida moderada (~55%)

Sin embargo, la infactibilidad surge por la **interacción compleja de múltiples restricciones**.

### Restricciones del Modelo

Recordemos las restricciones implementadas:

1. **R1 - Cobertura Exacta:** Σᵢ xᵢⱼₜ = rⱼₜ  
   → **Demanda debe cubrirse EXACTAMENTE** (no más, no menos)

2. **R2 - Disponibilidad:** xᵢⱼₜ ≤ 𝟙(cᵢⱼₜ > 0)  
   → Solo asignar si trabajador está disponible

3. **R3 - Máximo 2 turnos/día:** Σₜ xᵢⱼₜ ≤ 2  
   → Ningún trabajador puede hacer más de 2 turnos el mismo día

4. **R4 - No noche→mañana:** xᵢⱼ,noche + xᵢⱼ₊₁,mañana ≤ 1  
   → Descanso obligatorio entre turno noche y mañana siguiente

5. **R5 - No 3 fines de semana seguidos:** wᵢ,ₖ + wᵢ,ₖ₊₁ + wᵢ,ₖ₊₂ ≤ 2  
   → Límite de fines de semana consecutivos trabajados

---

## Causa Principal: Restricción R1 (Cobertura Exacta)

La **restricción más estricta** es **R1**, que requiere cobertura **EXACTA** de la demanda:

```
Σᵢ xᵢⱼₜ = rⱼₜ    (IGUALDAD, no ≥)
```

Esto significa:
- ❌ No se puede asignar más trabajadores de los requeridos
- ❌ No se puede asignar menos trabajadores de los requeridos
- ✅ Debe ser exactamente la cantidad demandada

### Impacto Combinado de Restricciones

La infactibilidad ocurre cuando:

1. **R1** fija exactamente cuántos trabajadores deben asignarse por turno
2. **R2** limita QUÉ trabajadores pueden asignarse (solo los disponibles)
3. **R4** elimina combinaciones válidas (trabajadores que hicieron turno noche no pueden hacer mañana al día siguiente)
4. **R3** limita cuántos turnos puede hacer cada trabajador por día
5. **R5** reduce aún más las opciones en fines de semana

### Ejemplo de Conflicto

Imaginemos un escenario simplificado en la Instancia 12:

```
Día 5 (viernes):
  - Demanda noche: 18 trabajadores
  - Disponibles para noche: 45 trabajadores

Día 6 (sábado):
  - Demanda mañana: 22 trabajadores
  - Disponibles para mañana: 48 trabajadores

Problema:
  - Si asignamos trabajadores {T1, T2, ..., T18} al turno noche del viernes
  - Por R4: Ninguno de ellos puede trabajar mañana del sábado
  - Quedan solo 48 - 18 = 30 trabajadores elegibles para mañana del sábado
  - Pero algunos de esos 30 pueden:
    * Ya haber trabajado 2 turnos el sábado (R3)
    * Estar llegando a 3 fines de semana consecutivos (R5)
    * No estar disponibles ese turno específico (R2)
  - Eventualmente no hay suficientes trabajadores válidos para satisfacer exactamente R1
```

---

## Análisis Específico de Conflictos

### Instancia 12

**Conflictos potenciales noche→mañana:** ~285 casos

Con 17 días y alta demanda de noche seguida de alta demanda de mañana, la restricción R4 crea un "cuello de botella" que propaga restricciones a lo largo de los días.

**Escenario problemático:**
- Días consecutivos con demanda alta tanto en noche como en mañana
- La restricción R4 reduce el pool de trabajadores elegibles para mañana
- Al exigir cobertura exacta (R1), no hay flexibilidad para compensar
- Resultado: imposible satisfacer todas las restricciones simultáneamente

### Instancia 15

**Conflictos potenciales noche→mañana:** ~323 casos

Similar a la instancia 12 pero con:
- Mayor demanda de turnos noche (426 total)
- Menor número de días (14 vs 17) → menos flexibilidad temporal
- Mayor concentración de demanda por día (~85 vs ~59)

**Factor agravante:**
- Con menos días, hay menos "espacio" para distribuir los trabajadores
- La restricción R5 (fines de semana) impacta más al haber menos opciones
- La combinación hace imposible una asignación factible

---

## ¿Por qué las otras 13 instancias SÍ son factibles?

Las instancias factibles tienen una o más de estas características:

1. **Mayor flexibilidad temporal:** Más días = más opciones para distribuir trabajadores
2. **Menor utilización:** Requieren menos del 50% de la capacidad disponible
3. **Mejor distribución de demanda:** Demanda más balanceada entre turnos y días
4. **Menos conflictos R4:** Menos casos de alta demanda noche seguida de alta demanda mañana
5. **Holgura en disponibilidad:** Suficientes trabajadores "de repuesto" para absorber las restricciones

---

## Conclusiones

### ¿Por qué son infactibles las instancias 12 y 15?

**Respuesta:** La **combinación estricta de restricciones** (especialmente R1 con R4) crea un problema de satisfacibilidad imposible para las configuraciones específicas de demanda y disponibilidad de estas instancias.

**Factores clave:**
1. ✗ **R1 (cobertura exacta)** no permite flexibilidad
2. ✗ **R4 (no noche→mañana)** elimina muchas combinaciones válidas
3. ✗ **Demanda concentrada** en días consecutivos
4. ✗ **Propagación de restricciones** a lo largo de los días
5. ✗ **Falta de "holgura"** para absorber conflictos

### ¿Es esto un problema del modelo o de las instancias?

**Es un problema de las instancias específicas**, no del modelo.

- El modelo es correcto y representa fielmente las restricciones del problema real
- El 86.7% de instancias son factibles, indicando que el modelo es razonable
- Las instancias 12 y 15 tienen configuraciones particulares que, aunque aparentemente viables, resultan infactibles bajo el conjunto completo de restricciones

### Recomendaciones para Evitar Infactibilidad

Para futuros generadores de instancias:

1. **Relajar R1:** Permitir Σᵢ xᵢⱼₜ ≥ rⱼₜ (cubrir al menos, no exactamente)
2. **Aumentar holgura:** Generar con ~20% más disponibilidad de la necesaria
3. **Balancear demanda:** Evitar picos altos en turnos consecutivos afectados por R4
4. **Validación previa:** Verificar factibilidad relajada antes de generar instancia completa
5. **Distribución inteligente:** Considerar restricciones al generar patrones de disponibilidad

---

## Referencias

- Resultados de ejecución: `../resultados/large/resultado_instancia_12.json`
- Resultados de ejecución: `../resultados/large/resultado_instancia_15.json`
- Script de análisis: `analizar_infactibilidad.py`
