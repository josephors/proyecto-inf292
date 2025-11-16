"""
Ejecutor_Solver_lpsolve_2_Grupo2_OPTI_SJ.py
Ejecutor batch del solver de asignación de turnos usando lpsolve55.

Este script automatiza la resolución de todas las instancias disponibles
(small, medium, large) y genera un resumen consolidado con estadísticas
de ejecución.

Funcionalidad:
  - Detecta todas las instancias JSON en data/
  - Ejecuta el solver (lpsolve55) por cada instancia
  - Guarda los resultados individuales en resultados/<tamano>/
  - Genera un resumen global
"""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent))
from Solver_lpsolve_2_Gruop2_OPTI_SJ import resolver_instancia


def ejecutar_todas_las_instancias():
    """
    Ejecuta el solver en todas las instancias disponibles y genera un resumen global.
    """

    instancias_dir = Path(__file__).parent / "data"
    resultados_dir = Path(__file__).parent / "resultados"

    tamanos = ["small", "medium", "large"]

    # Contenedor global
    resumen_total = {
        "fecha_ejecucion": datetime.now().isoformat(),
        "instancias_procesadas": 0,
        "instancias_optimas": 0,
        "instancias_infactibles": 0,
        "tiempo_total_segundos": 0.0,
        "resultados_por_tamano": {}
    }

    print("=" * 80)
    print("EJECUTANDO SOLVER EN TODAS LAS INSTANCIAS (lpsolve55)")
    print("=" * 80)
    print()

    # Crear directorios de resultados
    for tamano in tamanos:
        (resultados_dir / tamano).mkdir(parents=True, exist_ok=True)

    # Iterar por cada tamaño
    for tamano in tamanos:
        print(f"\n{'=' * 80}")
        print(f"Procesando instancias {tamano.upper()}")
        print(f"{'=' * 80}\n")

        instancias_path = instancias_dir / tamano
        archivos_json = sorted(instancias_path.glob("*.json"))

        resumen_tamano = {
            "total": len(archivos_json),
            "optimas": 0,
            "infactibles": 0,
            "tiempo_total": 0.0,
            "tiempo_promedio": 0.0,
            "instancias": []
        }

        for archivo in archivos_json:
            nombre_resultado = archivo.stem.replace("instancia", "resultado_instancia")
            ruta_salida = resultados_dir / tamano / f"{nombre_resultado}.json"

            print(f"Resolviendo {archivo.name}...")

            try:
                # Ejecutar solver individual
                resultado = resolver_instancia(str(archivo), str(ruta_salida))

                resumen_instancia = {
                    "archivo": archivo.name,
                    "estado": resultado["estado"],
                    "valor_objetivo": resultado["valor_objetivo"],
                    "tiempo_segundos": resultado["tiempo"],
                    "factible": resultado["estado"] == "Optimal"
                }

                resumen_tamano["instancias"].append(resumen_instancia)
                resumen_tamano["tiempo_total"] += resultado["tiempo"]

                # Actualizar contadores
                if resultado["estado"] == "Optimal":
                    resumen_tamano["optimas"] += 1
                    resumen_total["instancias_optimas"] += 1
                else:
                    resumen_tamano["infactibles"] += 1
                    resumen_total["instancias_infactibles"] += 1

                resumen_total["instancias_procesadas"] += 1
                resumen_total["tiempo_total_segundos"] += resultado["tiempo"]

            except Exception as e:
                print(f"ERROR al procesar {archivo}: {e}")
                resumen_tamano["infactibles"] += 1
                resumen_total["instancias_infactibles"] += 1

            print()

        # Promedio
        if resumen_tamano["total"] > 0:
            resumen_tamano["tiempo_promedio"] = (
                resumen_tamano["tiempo_total"] / resumen_tamano["total"]
            )

        resumen_total["resultados_por_tamano"][tamano] = resumen_tamano

        # Mostrar resumen por tamaño
        print(f"{'-' * 80}")
        print(f"RESUMEN {tamano.upper()}:")
        print(f"  Total instancias: {resumen_tamano['total']}")
        print(f"  Óptimas: {resumen_tamano['optimas']}")
        print(f"  Infactibles: {resumen_tamano['infactibles']}")
        print(f"  Tiempo total: {resumen_tamano['tiempo_total']:.2f}s")
        print(f"  Tiempo promedio: {resumen_tamano['tiempo_promedio']:.2f}s")
        print(f"{'-' * 80}\n")

    # Guardar resumen global
    resumen_path = resultados_dir / "resumen_ejecucion.json"
    with open(resumen_path, "w", encoding="utf-8") as f:
        json.dump(resumen_total, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("RESUMEN FINAL CONSOLIDADO")
    print("=" * 80)
    print(f"Total instancias procesadas: {resumen_total['instancias_procesadas']}")
    print(f"Instancias óptimas: {resumen_total['instancias_optimas']}")
    print(f"Instancias infactibles: {resumen_total['instancias_infactibles']}")
    print(f"Tiempo total: {resumen_total['tiempo_total_segundos']:.2f}s")
    print(f"\nResumen guardado en: {resumen_path}")
    print("=" * 80)


if __name__ == "__main__":
    ejecutar_todas_las_instancias()
