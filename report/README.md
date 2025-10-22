# Reporte LaTeX — Proyecto (OPTI_SJ · Grupo 2)

## Cómo compilar

### Requiere latexmk, TeX Live o MikTeX

Compilen como puedan, desde vs es mas facil...

## Bibliografía

Este proyecto usa `biblatex` con `biber` (configuración en `preamble.tex`) y el archivo de entradas es `references.bib` en este mismo directorio.

Cómo agregar una entrada a la bibliografía:

1. Abre `references.bib` y añade una entrada en formato BibTeX. Ejemplos:

```bibtex
@book{bertsimas1997introduction,
	title={Introduction to Linear Optimization},
	author={Bertsimas, D. and Tsitsiklis, J.},
	publisher={Athena Scientific},
	year={1997}
}

@misc{lpsolve,
	title = {lp\_solve reference guide},
	howpublished = {\url{https://lpsolve.sourceforge.net/}},
	note = {Accedido: 2025-10-21}
}
```

2. En el texto, referencia una entrada con `\cite{clave}` o `\autocite{clave}`. Ejemplo:

```tex
En este trabajo usamos lp\\_solve \cite{lpsolve} para resolver el modelo.
```

3. Si quieres listar todas las entradas del `.bib` aunque no estén citadas, añade `\nocite{*}` justo antes de `\printbibliography` en `report.tex`.

Comandos de compilación (desde el directorio `report/`):

Usando biblatex + biber (recomendado):
```bash
pdflatex report.tex
biber report
pdflatex report.tex
pdflatex report.tex
```

Flujo alternativo con BibTeX + natbib (si prefieres no usar biber):
- Revertir el preámbulo a `natbib` y usar `\bibliographystyle{...}` + `\bibliography{references}` en `report.tex`.
- Compilar con:
```bash
pdflatex report.tex
bibtex report
pdflatex report.tex
pdflatex report.tex
```

Notas:
- Asegúrate de ejecutar los comandos desde el directorio `report/` o ajusta las rutas.
- Si usas un editor (VS Code, TeXstudio), puedes configurar la herramienta para ejecutar el flujo biblatex/biber automáticamente.

## Cómo editar (flujo de equipo)
- **No edites** `report.tex` salvo para incluir/secuenciar secciones.
- Agrega/edita contenido en `sections/*.tex`.
- Actualiza los metadatos del equipo en `author.tex`.
- Citas con `\cite{clave}` y entradas en `references.bib`.

## Para Entrega 1
- Usa `00_resumen`, `01_modelo`, `02_generador`, `03_factibilidad`.
- Exporta/renombra el PDF final a **`Modelo_1_Grupo2_OPTI_SJ.pdf`** al empaquetar.

## Para Entrega 2
- Usa `00_resumen` (opcional) + `04_solver_lpsolve`, `05_analisis_resultados`, `06_tiempos`.