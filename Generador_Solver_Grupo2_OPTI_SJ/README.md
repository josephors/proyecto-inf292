# Instrucciones para la ejecución

Este proyecto contiene nuestro generador de instancias y solver para resolver problemas de asignación de turnos. A continuación, se describen los pasos para generar las instancias y obtener los resultados.

Dada la ausencia de requerimientos claros para la entrega y al parecer una luz verde a un trabajo mas investigativo, se mantiene el uso de json para la resolucion de las instancias a partir de la integracion de lpsolve en python, lo que permite un parseo mas sencillo de los datos generados.

## Estructura del proyecto

- **Generador de instancias**: `Generador_1_Grupo2_OPTI_SJ.py`
- **Solver**: `Ejecutor_Solver_lpsolve_2_Grupo2_OPTI_SJ` y `Solver_lpsolve_2_Gruop2_OPTI_SJ`
- **Carpeta de datos**: `data/` (contiene las instancias generadas)
- **Carpeta de resultados**: `resultados/` (almacena los resultados del solver)
- **Carpeta de analisis**: `analisis/`, almacena codigos generadores de plots usados 

## Requisitos

* Python 3.10 (recomendado).
* Entorno conda configurado con las siguientes dependencias instaladas mediante conda:
  * pandas
  * numpy
  * matplotlib
  * seaborn
  * jupyter
  * lpsolve55
* Utiliza conda install --file requirements.txt -c conda-forge

## Pasos para ejecutar

1. **Generar las instancias**:
   - Ejecuta el script del generador:
     ```bash
     python Generador_1_Grupo2_OPTI_SJ.py
     ```
   - Esto creará las instancias en la carpeta `data/` organizadas en subcarpetas `small`, `medium` y `large`.

2. **Resolver las instancias**:
   - Ejecuta el script del solver:
     ```bash
     python Ejecutor_Solver_lpsolve_2_Grupo2_OPTI_SJ
     ```
   - Esto procesará las instancias en `data/` y guardará los resultados en la carpeta `resultados/`.

3. **Ver los resultados**:
   - Los resultados individuales estarán en subcarpetas dentro de `resultados/`.
   - Un resumen global se generará en `resultados/resumen_ejecucion.json`.



## Notas

- Asegúrate de que las carpetas `data/` y `resultados/` existan antes de ejecutar los scripts.
- Si encuentras errores, verifica que las dependencias estén instaladas correctamente.
- Asegurate de instalar las dependencias mediante un entorno conda. Es necesario instalar Anaconda para la ejecucíon del proyecto, ya que es el medio por el cual se instaló el solver pedido (Lpsolve)

---

Para más detalles, consulta los comentarios en los scripts.