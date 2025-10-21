### (R1) Cobertura de turnos:
Asegurar que se cubra la demanda de cada turno:

$$
\sum_{i \in T} x_{i,j,t} = r_{j,t} \quad \forall j \in D, \forall t \in S
$$

### (R2) Disponibilidad individual:
Solo asignar si el trabajador está disponible:

$$
x_{i,j,t} \leq \mathbb{1}_{c_{i,j,t} > 0} \quad \forall i, j, t
$$

### (R3) Máximo dos turnos por día:

$$
\sum_{t \in S} x_{i,j,t} \leq 2 \quad \forall i \in T, \forall j \in D
$$

### (R4) No trabajar noche y mañana consecutiva:

$$
x_{i,j,\text{Noche}} + x_{i,j+1,\text{Mañana}} \leq 1 \quad \forall i \in T, \forall j \in D \setminus \{H\}
$$

### (R5) No trabajar tres fines de semana seguidos:

Definimos una variable auxiliar:

$$
w_{i,k} = \mathbb{1}_{\sum_{j \in \text{Finde}_k} \sum_{t \in S} x_{i,j,t} \geq 1}
$$

Y luego:

$$
w_{i,k} + w_{i,k+1} + w_{i,k+2} \leq 2 \quad \forall i \in T, \forall k \in \{1, \dots, K-2\}
$$