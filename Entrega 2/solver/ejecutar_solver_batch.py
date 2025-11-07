"""
Script para ejecutar el solver en todas las instancias y generar un resumen.
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# Añadir el directorio solver al path para importar
sys.path.append(str(Path(__file__).parent))

from solucionador_de_instancias_lpsolve import resolver_instancia


def ejecutar_todas_las_instancias():
    """
    Ejecuta el solver en todas las instancias y genera un resumen.
    """
    # Directorios
    base_dir = Path(__file__).parent.parent.parent
    instancias_dir = base_dir / "Entrega 1" / "generador" / "instancias"
    resultados_dir = base_dir / "Entrega 2" / "resultados"
    
    # Tamaños de instancias
    tamanos = ["small", "medium", "large"]
    
    # Resultados generales
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
    
    for tamano in tamanos:
        print(f"\n{'=' * 80}")
        print(f"Procesando instancias {tamano.upper()}")
        print(f"{'=' * 80}\n")
        
        # Buscar todas las instancias de este tamaño
        instancias_path = instancias_dir / tamano
        archivos_json = sorted(instancias_path.glob("*.json"))
        
        resumen_tamano = {
            "total": len(archivos_json),
            "optimas": 0,
            "infactibles": 0,
            "tiempo_total": 0,
            "tiempo_promedio": 0,
            "instancias": []
        }
        
        for archivo in archivos_json:
            # Determinar ruta de salida
            nombre_resultado = archivo.stem.replace("instancia", "resultado_instancia")
            ruta_salida = resultados_dir / tamano / f"{nombre_resultado}.json"
            
            try:
                # Resolver instancia
                resultado = resolver_instancia(str(archivo), str(ruta_salida))
                
                # Actualizar resumen
                resumen_instancia = {
                    "archivo": archivo.name,
                    "estado": resultado["estado"],
                    "valor_objetivo": resultado["valor_objetivo"],
                    "tiempo_segundos": resultado["tiempo"],
                    "factible": resultado["estado"] == "Optimal"
                }
                
                resumen_tamano["instancias"].append(resumen_instancia)
                resumen_tamano["tiempo_total"] += resultado["tiempo"]
                
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
        
        # Calcular tiempo promedio
        if resumen_tamano["total"] > 0:
            resumen_tamano["tiempo_promedio"] = resumen_tamano["tiempo_total"] / resumen_tamano["total"]
        
        resumen_total["resultados_por_tamano"][tamano] = resumen_tamano
        
        # Mostrar resumen del tamaño
        print(f"\n{'-' * 80}")
        print(f"RESUMEN {tamano.upper()}:")
        print(f"  Total instancias: {resumen_tamano['total']}")
        print(f"  Óptimas: {resumen_tamano['optimas']}")
        print(f"  Infactibles: {resumen_tamano['infactibles']}")
        print(f"  Tiempo total: {resumen_tamano['tiempo_total']:.2f}s")
        print(f"  Tiempo promedio: {resumen_tamano['tiempo_promedio']:.2f}s")
        print(f"{'-' * 80}\n")
    
    # Guardar resumen total
    resumen_path = resultados_dir / "resumen_ejecucion.json"
    with open(resumen_path, 'w', encoding='utf-8') as f:
        json.dump(resumen_total, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen final
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
