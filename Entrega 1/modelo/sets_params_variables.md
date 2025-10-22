## 1. Conjuntos e Índices

- **T**: conjunto de trabajadores, indexado por *i ∈ T*
- **D = {1, 2, ..., H}**: conjunto de días del horizonte de planificación, indexado por *j ∈ D*
- **S**: conjunto de turnos disponibles por día, indexado por *t ∈ S*  
  - Para instancias pequeñas: S = {Día, Noche}  
  - Para medianas y grandes: S = {Mañana, Tarde, Noche}

---

## 2. Parámetros

- **H ∈ ℕ**: número total de días del horizonte de planificación
- **cᵢⱼₜ ∈ {0,1,…,10}**: disposición del trabajador *i* para trabajar el día *j* en el turno *t*
- **rⱼₜ ∈ ℕ**: número de trabajadores requeridos para el día *j* y turno *t*
- **Wⱼ ∈ {0,1}**: indicador si el día *j* es fin de semana (sábado o domingo)

---

## 3. Variables de decisión

- **xᵢⱼₜ ∈ {0,1}**: vale 1 si el trabajador *i* es asignado al turno *t* del día *j*, y 0 en otro caso
