"""Build downloads/canon6d_photo_planner_assets.zip from the current artefacts.

The bundle used to be assembled by hand and went stale (it still shipped the
pre-correction plan pages). It is now rebuilt on every regeneration, with a
fixed timestamp, sorted members and no compression so the bytes depend only
on the inputs: PNG and WebP are already compressed, and zlib output can differ
between machines, which would break `regenerate_all.py && git diff --exit-code`.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "downloads" / "canon6d_photo_planner_assets.zip"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)

README = """# FocalRuta · recursos para llevar

Seis planes fotográficos por Lima para Canon EOS 6D, listos para usar sin conexión.

## Qué hay aquí

- `plans/plan_a.html` … `{last}.html`: cada plan con sus 10 tomas, diagramas y
  ajustes para día, tarde y noche. Se abren en cualquier navegador, también en el
  iPhone desde la app Archivos.
- `field_card.html`: la tarjeta de campo para imprimir o llevar en el teléfono.
- `diagrams/`: los 120 diagramas de las tomas (persona y perro) y {extra} diagramas de
  composición y comparación de lentes, en PNG para imprimir.
- `data/plans.json`: todos los datos de los planes, por si quieres usarlos en otra
  herramienta.

## Cómo leer los ajustes

Cada toma trae ajustes distintos para día, tarde y noche. Están calculados para la
luz típica de cada escena (tabla de valores de exposición ANSI PH2.7) y, cuando hace
falta, indican el filtro ND necesario (por ejemplo, «ND de 6 pasos (ND64)»). Si una
toma dice «no viable» a esa hora, cámbiala de horario. Son un punto de partida:
haz una foto de prueba y revisa el histograma.

La profundidad de campo usa un círculo de confusión de 0.03 mm, la convención
habitual para full frame; tómala como guía de planificación, no como un borde exacto.
"""


def readme() -> str:
    """The README with this build's plans and diagrams counted (W08)."""
    import json
    import plan_counts
    data = json.loads((ROOT / "data" / "plans.json").read_text(encoding="utf-8"))
    c = plan_counts.counts(data, ROOT)
    text = README.replace("{last}", data["plans"][-1]["id"]).replace("{extra}", str(c["all_diagrams"] - c["diagrams"]))
    return plan_counts.fill(text, c)


def members() -> list[tuple[str, Path]]:
    items = [("field_card.html", ROOT / "field_card.html"),
             ("data/plans.json", ROOT / "data" / "plans.json")]
    items += [(f"plans/{p.name}", p) for p in sorted((ROOT / "plans").glob("plan_*.html"))]
    items += [(f"diagrams/{p.name}", p) for p in sorted((ROOT / "diagrams").glob("*.png"))]
    return items


def write_member(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w") as archive:
        write_member(archive, "LEEME.md", readme().encode("utf-8"))
        for name, path in members():
            write_member(archive, name, path.read_bytes())
    print(f"{OUT.relative_to(ROOT)}: {len(members()) + 1} files, {OUT.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
