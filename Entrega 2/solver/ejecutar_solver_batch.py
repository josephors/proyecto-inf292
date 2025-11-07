"""
Ejecutor batch del solver de asignación de turnos.

Este script automatiza la resolución de todas las instancias disponibles
(small, medium, large) y genera un resumen consolidado con estadísticas
de ejecución.

Funcionalidad:
  - Localiza automáticamente todas las instancias JSON en Entrega 1
  - Ejecuta el solver sobre cada instancia
  - Guarda los resultados individuales en Entrega 2/resultados/
  - Genera un resumen global con tiempos y estados
  - Calcula estadísticas por tamaño (small/medium/large)

Uso:
    python ejecutar_solver_batch.py
"""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent))
from solucionador_de_instancias_lpsolve import resolver_instancia


def ejecutar_todas_las_instancias():
    """
    Ejecuta el solver en todas las instancias disponibles y genera resumen.
    
    Recorre las carpetas small/medium/large en Entrega 1/generador/instancias/,
    resuelve cada instancia JSON encontrada, guarda los resultados individuales
    en Entrega 2/resultados/ y produce un archivo resumen_ejecucion.json con
    estadísticas globales y por tamaño.
    
    El resumen incluye:
      - Número de instancias procesadas, óptimas e infactibles
      - Tiempos totales y promedios por tamaño
      - Detalle por instancia (estado, valor objetivo, tiempo)
    """
    # Localizar directorios del proyecto
    base_dir = Path(__file__).parent.parent.parent
    instancias_dir = base_dir / "Entrega 1" / "generador" / "instancias"
    resultados_dir = base_dir / "Entrega 2" / "resultados"
    
    tamanos = ["small", "medium", "large"]
    
    # Estructura para acumular estadísticas globales
    resumen_total = {
        "fecha_ejecucion": datetime.now().isoformat(),
        "instancias_procesadas": 0,
        "instancias_optimas": 0,
        "instancias_infactibles": 0,
        "tiempo_total_segundos": 0,
        "resultados_por_tamano": {}
    }
    
    print("=" * 80)
    print("EJECUTANDO SOLVER EN TODAS LAS INSTANCIAS")
    print("=" * 80)
    print()
    
    # Procesar cada tamaño de instancia
    for tamano in tamanos:
        print(f"\n{'=' * 80}")
        print(f"Procesando instancias {tamano.upper()}")
        print(f"{'=' * 80}\n")
        
        # Buscar todos los archivos JSON en el directorio del tamaño actual
        instancias_path = instancias_dir / tamano
        archivos_json = sorted(instancias_path.glob("*.json"))
        
        # Estructura para acumular estadísticas de este tamaño
        resumen_tamano = {
            "total": len(archivos_json),
            "optimas": 0,
            "infactibles": 0,
            "tiempo_total": 0,
            "tiempo_promedio": 0,
            "instancias": []
        }
        
        # Resolver cada instancia del tamaño actual
        for archivo in archivos_json:
            # Construir nombre del archivo de resultado
            nombre_resultado = archivo.stem.replace("instancia", "resultado_instancia")
            ruta_salida = resultados_dir / tamano / f"{nombre_resultado}.json"
            
            try:
                # Invocar el solver
                resultado = resolver_instancia(str(archivo), str(ruta_salida))
                
                # Registrar resultado de esta instancia
                resumen_instancia = {
                    "archivo": archivo.name,
                    "estado": resultado["estado"],
                    "valor_objetivo": resultado["valor_objetivo"],
                    "tiempo_segundos": resultado["tiempo"],
                    "factible": resultado["estado"] == "Optimal"
                }
                
                resumen_tamano["instancias"].append(resumen_instancia)
                resumen_tamano["tiempo_total"] += resultado["tiempo"]
                
                # Actualizar contadores globales y por tamaño
                if resultado["estado"] == "Optimal":
                    resumen_tamano["optimas"] += 1
                    resumen_total["instancias_optimas"] += 1
                else:
                    resumen_tamano["infactibles"] += 1
                    resumen_total["instancias_infactibles"] += 1
                
                resumen_total["instancias_procesadas"] += 1
                resumen_total["tiempo_total_segundos"] += resultado["tiempo"]
                
                print()
                
            except Exception as e:
                print(f"ERROR al procesar {archivo}: {e}")
                print()
        
        # Calcular estadística promedio para este tamaño
        if resumen_tamano["total"] > 0:
            resumen_tamano["tiempo_promedio"] = resumen_tamano["tiempo_total"] / resumen_tamano["total"]
        
        # Guardar estadísticas de este tamaño en el resumen global
        resumen_total["resultados_por_tamano"][tamano] = resumen_tamano
        
        # Mostrar resumen por pantalla
        print(f"\n{'-' * 80}")
        print(f"RESUMEN {tamano.upper()}:")
        print(f"  Total instancias: {resumen_tamano['total']}")
        print(f"  Óptimas: {resumen_tamano['optimas']}")
        print(f"  Infactibles: {resumen_tamano['infactibles']}")
        print(f"  Tiempo total: {resumen_tamano['tiempo_total']:.2f}s")
        print(f"  Tiempo promedio: {resumen_tamano['tiempo_promedio']:.2f}s")
        print(f"{'-' * 80}\n")
    
    # Guardar resumen global en JSON
    resumen_path = resultados_dir / "resumen_ejecucion.json"
    with open(resumen_path, 'w', encoding='utf-8') as f:
        json.dump(resumen_total, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen final consolidado
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"Total instancias procesadas: {resumen_total['instancias_procesadas']}")
    print(f"Instancias óptimas: {resumen_total['instancias_optimas']}")
    print(f"Instancias infactibles: {resumen_total['instancias_infactibles']}")
    print(f"Tiempo total: {resumen_total['tiempo_total_segundos']:.2f}s")
    print(f"\nResumen guardado en: {resumen_path}")
    print("=" * 80)


if __name__ == "__main__":
    ejecutar_todas_las_instancias()
