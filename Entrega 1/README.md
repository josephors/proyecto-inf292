# Entrega 1 — Modelo matemático + Generador de instancias

**Curso/Sección:** OPTI_SJ  
**Grupo:** 2  
**Alcance:**  
- Parte 1: Modelo matemático (conjuntos, parámetros, variables, objetivo, restricciones, explicación breve).  
- Parte 2: Generador de instancias (5 por tamaño; demandas ~ Normal; disposiciones ~ Uniforme entera 0–10).

## Estructura sugerida
Entrega1/
├─ README.md
├─ modelo/                 # notas técnicas y bosquejos para pasar al informe
│  ├─ sets_params_variables.md
│  ├─ restricciones.md
│  └─ funcion_objetivo.md
├─ generador/
│  ├─ src/
│  │  ├─ Generador_1_Grupo2_OPTI_SJ.py   # nombre conforme a enunciado
│  │  ├─ requirements.txt
│  │  └─ utils.py
│  └─ instances/
│     ├─ small/  ├─ medium/  └─ large/
└─ empaquetado/
   └─ build_zip.sh
   
## Cómo trabajar
1. Diseñar el **modelo** en `Entrega1/modelo/` y traspasar al `report/sections/01_modelo.tex`.  
2. Implementar el **generador** en `generador/src/` (mantener nombre de archivo).  
3. Generar **instancias** en `generador/instances/` (subcarpetas por tamaño).  
4. Compilar el informe en `report/` (ver `report/README.md`).  
5. Ejecutar `empaquetado/build_zip.sh` para crear el `.zip` final con:  
   - `Modelo_1_Grupo2_OPTI_SJ.pdf`  
   - `Generador_1_Grupo2_OPTI_SJ.py` (+ archivos auxiliares si corresponde)

## Convenciones
- Disposición `p_{i,d,t} ∈ {0,…,10}` (0 = no puede).  
- Demandas `r_{d,t}` por día–turno ~ Normal truncada a enteros ≥ 0.  
- 5 instancias por tamaño: *small, medium, large* (rangos del enunciado).