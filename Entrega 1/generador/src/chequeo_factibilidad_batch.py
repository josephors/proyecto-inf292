# src/chequeo_factibilidad.py
# -*- coding: utf-8 -*-
"""
Checks A/B/C + auto-fix + reporte 4.3 + reemplazo en ../instancias/<tipo>/instancia_<id>.json
y limpieza de salidas por ejecución para no acumular archivos.

Uso típico:
    python src/chequeo_factibilidad.py \
        --base_dir ../instancias --out_dir ../reporte \
        --tipos small medium large \
        --auto_fix --max_turnos_dia 2 \
        --clean_outputs --clean_backups --backup_originals
"""

import json
import math
import statistics
import logging
from pathlib import Path
from copy import deepcopy
from collections import defaultdict
import argparse
import shutil

# ----------------- Utilidades -----------------

WEEKDAY_OFFSET = {
    "lunes": 0, "martes": 1, "miercoles": 2, "miércoles": 2,
    "jueves": 3, "viernes": 4, "sabado": 5, "sábado": 5, "domingo": 6
}

def _dia_num_from_nombre(nombre_dia: str):
    try:
        nombre, semana = nombre_dia.split("_")
        semana = int(semana)
        off = WEEKDAY_OFFSET[nombre.lower()]
        return (semana - 1) * 7 + off + 1
    except Exception:
        return None

def _sum_dict_values(d):
    return sum(d.values()) if d else 0

def _scale_demands_proportionally(demands_dict, target_sum):
    if target_sum < 0:
        target_sum = 0
    current_sum = _sum_dict_values(demands_dict)
    if current_sum == 0:
        for k in demands_dict:
            demands_dict[k] = 0
        return demands_dict
    factor = target_sum / current_sum
    scaled, residues = {}, []
    for k, v in demands_dict.items():
        raw = v * factor
        flo = math.floor(raw)
        scaled[k] = flo
        residues.append((k, raw - flo, v))
    deficit = target_sum - _sum_dict_values(scaled)
    residues.sort(key=lambda x: (x[1], x[2]), reverse=True)
    for i in range(deficit):
        if i < len(residues):
            k = residues[i][0]
            scaled[k] += 1
    return scaled

def _compute_avail_por_turno(disposicion, dia_num):
    avail = defaultdict(int)
    if dia_num is None:
        return {}
    for fila in disposicion:
        if fila['dia'] == dia_num and fila['disposicion'] > 0:
            avail[fila['turno']] += 1
    return dict(avail)

def _is_finde(nombre_dia: str) -> bool:
    nd = nombre_dia.lower()
    return nd.startswith("sabado") or nd.startswith("sábado") or nd.startswith("domingo")

def _collect_turnos(demanda_dias):
    turnos = set()
    for _, demandas in demanda_dias.items():
        for turno in demandas.keys():
            turnos.add(turno)
    return turnos

# ----------------- Limpieza de salidas -----------------

def limpiar_salida(out_dir: Path, clean_backups: bool = False):
    """
    Elimina archivos de salida generados por este script para no acumular:
    - resumen_*.json
    - (opcional) carpeta backups/ completa
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    eliminados = 0

    # Borrar resúmenes
    for p in out_dir.glob("resumen_*.json"):
        try:
            p.unlink()
            eliminados += 1
        except Exception as e:
            logging.warning(f"No se pudo eliminar {p}: {e}")

    # Borrar backups si se pidió
    backups_dir = out_dir / "backups"
    if clean_backups and backups_dir.exists():
        try:
            shutil.rmtree(backups_dir)
            logging.info(f"Backups eliminados: {backups_dir}")
        except Exception as e:
            logging.warning(f"No se pudo eliminar la carpeta de backups {backups_dir}: {e}")

    logging.info(f"Archivos de resumen eliminados: {eliminados}")

# ----------------- Checks + Auto-fix -----------------

def apply_checks_with_autofix(instancia, max_turnos_por_dia_por_trabajador=2, auto_fix=True):
    trabajadores = int(instancia["trabajadores"])
    disposicion = instancia["disposicion"]
    demanda_dias = deepcopy(instancia["demanda_dias"])

    # Primera pasada: detectar fallos
    check_A_ok = True
    check_B_ok = True
    check_C_ok = True

    for nombre_dia, demandas_turnos in demanda_dias.items():
        dia_num = _dia_num_from_nombre(nombre_dia)
        avail_por_turno = _compute_avail_por_turno(disposicion, dia_num)
        for turno, demanda in demandas_turnos.items():
            if demanda > avail_por_turno.get(turno, 0):
                check_A_ok = False

    capacidad_dia = max_turnos_por_dia_por_trabajador * trabajadores
    for _, demandas_turnos in demanda_dias.items():
        if sum(demandas_turnos.values()) > capacidad_dia:
            check_B_ok = False

    finde_dias = [d for d in demanda_dias.keys() if _is_finde(d)]
    if finde_dias:
        total_demanda_finde = sum(sum(demanda_dias[d].values()) for d in finde_dias)
        capacidad_finde = capacidad_dia * len(finde_dias)
        if total_demanda_finde > capacidad_finde:
            check_C_ok = False

    flags_before = {
        "check_A_ok": check_A_ok,
        "check_B_ok": check_B_ok,
        "check_C_ok": check_C_ok
    }

    fixes_applied = {"A_recortes": 0, "B_escalados_dia": 0, "C_escalado_finde": 0}
    hubo_cambios = False

    # Reparación
    if auto_fix:
        for nombre_dia, demandas_turnos in demanda_dias.items():
            dia_num = _dia_num_from_nombre(nombre_dia)
            avail_por_turno = _compute_avail_por_turno(disposicion, dia_num)
            for turno, demanda in list(demandas_turnos.items()):
                disp = avail_por_turno.get(turno, 0)
                if demanda > disp:
                    demanda_dias[nombre_dia][turno] = disp
                    fixes_applied["A_recortes"] += 1
                    hubo_cambios = True

        for nombre_dia, demandas_turnos in list(demanda_dias.items()):
            suma = sum(demandas_turnos.values())
            if suma > capacidad_dia:
                demanda_dias[nombre_dia] = _scale_demands_proportionally(demandas_turnos, capacidad_dia)
                fixes_applied["B_escalados_dia"] += 1
                hubo_cambios = True

        finde_dias = [d for d in demanda_dias.keys() if _is_finde(d)]
        if finde_dias:
            total_demanda_finde = sum(sum(demanda_dias[d].values()) for d in finde_dias)
            capacidad_finde = capacidad_dia * len(finde_dias)
            if total_demanda_finde > capacidad_finde:
                factor = capacidad_finde / total_demanda_finde if total_demanda_finde > 0 else 0.0
                sum_dias_orig = [sum(demanda_dias[d].values()) for d in finde_dias]
                targets = [int(round(s * factor)) for s in sum_dias_orig]
                diff = capacidad_finde - sum(targets)
                residuos = []
                for d, s in zip(finde_dias, sum_dias_orig):
                    raw = s * factor
                    residuos.append((d, raw - math.floor(raw), s))
                residuos.sort(key=lambda x: (x[1], x[2]), reverse=True)
                for i in range(abs(diff)):
                    if i < len(residuos):
                        d = residuos[i][0]
                        idx = finde_dias.index(d)
                        targets[idx] += 1 if diff > 0 else -1
                        if targets[idx] < 0:
                            targets[idx] = 0
                for d, target in zip(finde_dias, targets):
                    demanda_dias[d] = _scale_demands_proportionally(demanda_dias[d], target)
                fixes_applied["C_escalado_finde"] += 1
                hubo_cambios = True

    # Segunda pasada: verificar
    check_A2_ok = True
    check_B2_ok = True
    check_C2_ok = True

    for nombre_dia, demandas_turnos in demanda_dias.items():
        dia_num = _dia_num_from_nombre(nombre_dia)
        avail_por_turno = _compute_avail_por_turno(disposicion, dia_num)
        for turno, demanda in demandas_turnos.items():
            if demanda > avail_por_turno.get(turno, 0):
                check_A2_ok = False

    for _, demandas_turnos in demanda_dias.items():
        if sum(demandas_turnos.values()) > capacidad_dia:
            check_B2_ok = False

    finde_dias = [d for d in demanda_dias.keys() if _is_finde(d)]
    if finde_dias:
        total_demanda_finde = sum(sum(demanda_dias[d].values()) for d in finde_dias)
        capacidad_finde = capacidad_dia * len(finde_dias)
        if total_demanda_finde > capacidad_finde:
            check_C2_ok = False

    flags_after = {
        "check_A_ok": check_A2_ok,
        "check_B_ok": check_B2_ok,
        "check_C_ok": check_C2_ok
    }

    return demanda_dias, flags_before, flags_after, fixes_applied, hubo_cambios

# ----------------- Estadísticos 4.3 -----------------

def generar_resumen_43(instancia, demanda_dias_fix, flags_before, flags_after, fixes_applied,
                       auto_fix=True, overwrote=False, original_path=None, backup_path=None):
    trabajadores = int(instancia["trabajadores"])
    dias = int(instancia["dias"])
    disposicion = instancia["disposicion"]

    turnos_set = _collect_turnos(demanda_dias_fix)
    card_T = trabajadores
    H = dias
    card_S = len(turnos_set)

    c_vals = [fila['disposicion'] for fila in disposicion]
    c_min = min(c_vals) if c_vals else None
    c_max = max(c_vals) if c_vals else None
    c_avg = round(statistics.mean(c_vals), 3) if c_vals else None
    c_zeros_pct = round(100.0 * sum(1 for v in c_vals if v == 0) / len(c_vals), 2) if c_vals else None

    r_vals = []
    for _, demandas_turnos in demanda_dias_fix.items():
        r_vals.extend(list(demandas_turnos.values()))
    r_min = min(r_vals) if r_vals else None
    r_max = max(r_vals) if r_vals else None
    r_avg = round(statistics.mean(r_vals), 3) if r_vals else None

    resumen = {
        "id_instancia": instancia.get("id_instancia"),
        "tipo": instancia.get("tipo"),
        "card_T": card_T,
        "H": H,
        "card_S": card_S,
        "c_min": c_min,
        "c_max": c_max,
        "c_avg": c_avg,
        "c_pct_zeros": c_zeros_pct,
        "r_min": r_min,
        "r_max": r_max,
        "r_avg": r_avg,
        "checks_before": flags_before,
        "checks_after": flags_after,
        "auto_fix": auto_fix,
        "fixes_applied": fixes_applied,
        "all_checks_ok": all(flags_after.values()),
        "overwrote_original": overwrote,
        "original_path": str(original_path) if original_path else None,
        "backup_path": str(backup_path) if backup_path else None
    }
    return resumen

# ----------------- Pipeline secuencial -----------------

def procesar_archivo_instancia(archivo_json: Path,
                               out_dir: Path,
                               auto_fix=True,
                               max_turnos_por_dia_por_trabajador=2,
                               backup_originals=False):
    instancia = json.loads(archivo_json.read_text(encoding="utf-8"))

    demanda_dias_fix, flags_before, flags_after, fixes_applied, hubo_cambios = apply_checks_with_autofix(
        instancia,
        max_turnos_por_dia_por_trabajador=max_turnos_por_dia_por_trabajador,
        auto_fix=auto_fix
    )

    backup_path = None
    overwrote = False

    if hubo_cambios and auto_fix:
        if backup_originals:
            backups_dir = out_dir / "backups"
            backups_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backups_dir / archivo_json.name
            shutil.copy2(archivo_json, backup_path)

        instancia_reparada = deepcopy(instancia)
        instancia_reparada["demanda_dias"] = demanda_dias_fix
        instancia_reparada["metadata_fixes"] = {
            "checks_before": flags_before,
            "checks_after": flags_after,
            "fixes_applied": fixes_applied
        }
        archivo_json.write_text(json.dumps(instancia_reparada, ensure_ascii=False, indent=4), encoding="utf-8")
        overwrote = True

    resumen = generar_resumen_43(
        instancia, demanda_dias_fix, flags_before, flags_after, fixes_applied,
        auto_fix=auto_fix, overwrote=overwrote, original_path=archivo_json, backup_path=backup_path
    )

    base_id = instancia.get("id_instancia", archivo_json.stem.replace("instancia_", ""))
    resumen_path = out_dir / f"resumen_{base_id}.json"
    resumen_path.write_text(json.dumps(resumen, ensure_ascii=False, indent=4), encoding="utf-8")

    return resumen

def recorrer_carpeta_instancias(base_dir, out_dir, tipos, auto_fix=True,
                                max_turnos_por_dia_por_trabajador=2,
                                backup_originals=False):
    base_path = Path(base_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    n_total, n_ok, n_overwritten = 0, 0, 0

    for tipo in tipos:
        carpeta = base_path / tipo
        if not carpeta.exists():
            logging.warning(f"No existe carpeta: {carpeta}")
            continue

        for archivo in carpeta.glob("instancia_*.json"):
            n_total += 1
            resumen = procesar_archivo_instancia(
                archivo_json=archivo,
                out_dir=out_path,
                auto_fix=auto_fix,
                max_turnos_por_dia_por_trabajador=max_turnos_por_dia_por_trabajador,
                backup_originals=backup_originals
            )
            if resumen["overwrote_original"]:
                n_overwritten += 1
            if resumen["all_checks_ok"]:
                n_ok += 1

            logging.info(
                f"[{tipo}] {archivo.name} | "
                f"OK(after)={resumen['all_checks_ok']} | "
                f"overwrote={resumen['overwrote_original']} | "
                f"fixes={resumen['fixes_applied']}"
            )

    logging.info(f"Procesadas: {n_total} | All checks OK: {n_ok} | Sobrescritas: {n_overwritten}")

# ----------------- CLI -----------------

def parse_args():
    parser = argparse.ArgumentParser(description="Checks A/B/C + auto-fix + reporte 4.3 (sobrescribe instancias si repara) + limpieza por ejecución")
    parser.add_argument("--base_dir", default="../instancias", help="Carpeta base de instancias (contiene small/medium/large)")
    parser.add_argument("--out_dir", default="../reporte", help="Carpeta de salida para reportes")
    parser.add_argument("--tipos", nargs="*", default=["small","medium","large"], help="Subcarpetas a procesar")
    parser.add_argument("--auto_fix", action="store_true", default=True, help="Aplicar reparaciones automáticas")
    parser.add_argument("--max_turnos_dia", type=int, default=2, help="Capacidad por trabajador por día (e.g., 2)")
    parser.add_argument("--backup_originals", action="store_true", help="Guardar copia del JSON original antes de sobrescribir")
    parser.add_argument("--clean_outputs", action="store_true", help="Eliminar resúmenes previos (resumen_*.json) en out_dir antes de procesar")
    parser.add_argument("--clean_backups", action="store_true", help="Eliminar carpeta backups/ en out_dir antes de procesar")
    return parser.parse_args()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()

    out_path = Path(args.out_dir)
    if args.clean_outputs:
        limpiar_salida(out_path, clean_backups=args.clean_backups)

    recorrer_carpeta_instancias(
        base_dir=args.base_dir,
        out_dir=args.out_dir,
        tipos=tuple(args.tipos),
        auto_fix=args.auto_fix,
        max_turnos_por_dia_por_trabajador=args.max_turnos_dia,
        backup_originals=args.backup_originals
    )

    print(f"Listo. Resúmenes en {args.out_dir}")