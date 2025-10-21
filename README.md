# Proyecto OPTI — OPTI_SJ · Grupo 2

Este repositorio contiene el desarrollo del proyecto de **Fundamentos de Investigación de Operaciones — Optimización**.  
El objetivo es modelar y resolver un problema de asignación de personal por día–turno maximizando la **disposición total** de los trabajadores, cumpliendo **cobertura** y restricciones de **bienestar/operativas**.

> **Asignación:** Grupo 2 — Sección **OPTI_SJ** — **Solver: lpsolve** (para la Entrega 2).

# Pendientes:
- Usar issues 

## Estructura del repositorio (vista rápida)

```
.
├─ Entrega1/                # Parte 1 (modelo) + Parte 2 (generador de instancias)
│  ├─ README.md
│  ├─ modelo/
│  ├─ generador/
│  │  ├─ src/
│  │  └─ instances/         # small/ medium/ large/
│  └─ empaquetado/
│     └─ build_zip.sh       # crea Entrega_1_Grupo2_OPTI_SJ.zip
│
├─ Entrega2/                # Parte 3 (solver) + Parte 4 y 5 (análisis y tiempos)
│  ├─ README.md
│  ├─ solver/
│  │  └─ lpsolve/
│  │     ├─ model.lp
│  │     ├─ data/           # inputs derivados de instancias
│  │     └─ run.sh          # resolución por lotes
│  ├─ analisis/             # notebooks, gráficos, tablas
│  └─ resultados/           # soluciones y logs por tamaño
│
└─ report/                  # Informe LaTeX (usado en ambas entregas)
   ├─ README.md
   ├─ report.tex            # documento principal
   ├─ preamble.tex          # paquetes/estilo
   ├─ author.tex            # datos del equipo
   ├─ references.bib        # bibliografía
   └─ sections/             # secciones del informe
      ├─ 00_resumen.tex
      ├─ 01_modelo.tex
      ├─ 02_generador.tex
      ├─ 03_factibilidad.tex
      ├─ 04_solver_lpsolve.tex
      ├─ 05_analisis_resultados.tex
      └─ 06_tiempos.tex
```

## Roadmap por entregas

### Entrega 1 (Modelo + Generador)
- **Parte 1**: Modelo matemático (conjuntos, parámetros, variables, objetivo, restricciones, breve explicación).
- **Parte 2**: Generador de instancias (5 por tamaño: pequeñas/medianas/grandes).
- **Informe** (máx. 6 páginas):
  - 1 portada, 2 modelo, 2 generador, 1 factibilidad.
- **Entrega**: ZIP llamado `Entrega_1_Grupo2_OPTI_SJ.zip` conteniendo:
  - `Modelo_1_Grupo2_OPTI_SJ.pdf`
  - `Generador_1_Grupo2_OPTI_SJ.py` (+ auxiliares si aplica)
- **Empaquetado**: usar `Entrega1/empaquetado/build_zip.sh`.

### Entrega 2 (lpsolve + Análisis y Tiempos)
- **Parte 3**: Modelo `.lp` para lpsolve + pipeline de carga de datos.
- **Parte 4**: Análisis de resultados (objetivo vs tamaño, infactibilidades, calendarios gráficos para instancias pequeñas).
- **Parte 5**: Tiempos de resolución vs tamaño.
- **Entrega**: (no hay nombre de ZIP exigido en el enunciado). Sugerimos empaquetar como:
  - `Entrega_2_Grupo2_OPTI_SJ.zip` con:
    - PDF final (report)
    - `solver/lpsolve/` (modelos, scripts, data mínima reproducible)
    - `analisis/` (notebooks/figuras)
    - `resultados/` (CSV/JSON y logs)


### Requisitos sugeridos
- **Python 3.10+** (para generador y análisis).
- **lp_solve** (CLI o bindings).
- **LaTeX** con `latexmk` (para compilar reportes).
- **Git** (flujo colaborativo).

### Entornos recomendados
```bash
# Crear venv para generador y análisis
python3 -m venv .venv && source .venv/bin/activate
pip install -r Entrega1/generador/src/requirements.txt  # si aplica
```
