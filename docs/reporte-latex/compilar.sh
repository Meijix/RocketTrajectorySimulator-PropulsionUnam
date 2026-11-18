#!/bin/sh
# Genera el PDF del reporte.
#   1. Convierte ../reporte-xitle2.md a contenido.tex con pandoc.
#   2. Compila main.tex dos veces con lualatex (la segunda arma el índice).
# Las figuras se generan aparte con: python docs/reporte-latex/generar_figuras.py
set -e
cd "$(dirname "$0")"

pandoc ../reporte-xitle2.md --from markdown --to latex --shift-heading-level-by=-1 --columns=60 --syntax-highlighting=none \
  | sed 's#reporte-latex/figuras/#figuras/#g' > contenido.tex

lualatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
lualatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
mv main.pdf reporte-xitle2.pdf
rm -f main.aux main.log main.out main.toc
echo "PDF generado: $(pwd)/reporte-xitle2.pdf"
