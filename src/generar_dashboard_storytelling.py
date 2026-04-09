#!/usr/bin/env python3
"""Genera un dashboard HTML con gráficos y storytelling del dataset y métricas de sesgo.

Sin dependencias externas: usa solo librerías estándar.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

DATA_PATH = Path("data/women_divulgacion_ai_generativa_cuantica_2024_2026.csv")
METRICS_PATH = Path("results/metricas_modelo_sesgo.json")
OUT_PATH = Path("reports/dashboard_storytelling.html")


PALETTE = {
    "ia_generativa": "#6366f1",
    "computacion_cuantica": "#14b8a6",
    "global": "#0ea5e9",
    "europa": "#f59e0b",
    "usa": "#ef4444",
    "asia": "#22c55e",
    "ingles": "#8b5cf6",
    "multilingue": "#f97316",
}


def load_rows() -> list[dict[str, str]]:
    with DATA_PATH.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def safe_color(key: str, fallback: str = "#64748b") -> str:
    return PALETTE.get(key.lower(), fallback)


def yearly_domain_counts(rows: list[dict[str, str]]):
    counts = defaultdict(Counter)
    for r in rows:
        year = r["fecha"].split("-")[0]
        counts[year][r["dominio"]] += 1
    return dict(sorted(counts.items(), key=lambda x: x[0]))


def build_stacked_bar_svg(year_counts: dict[str, Counter], width=680, height=280) -> str:
    years = list(year_counts.keys())
    max_total = max(sum(c.values()) for c in year_counts.values()) if year_counts else 1

    chart_top = 20
    chart_bottom = height - 40
    chart_height = chart_bottom - chart_top
    left = 70
    right = width - 20
    inner_width = right - left
    gap = 26
    bar_w = (inner_width - gap * (len(years) - 1)) / max(len(years), 1)

    elements = [f'<rect x="0" y="0" width="{width}" height="{height}" fill="#0b1020" rx="16"/>']

    # grid lines + y labels
    for i in range(5):
        val = round(max_total * i / 4)
        y = chart_bottom - (chart_height * i / 4)
        elements.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#1f2a44" stroke-width="1"/>')
        elements.append(f'<text x="{left - 10}" y="{y + 4:.1f}" fill="#9fb0d9" font-size="11" text-anchor="end">{val}</text>')

    domains = ["ia_generativa", "computacion_cuantica"]

    for idx, year in enumerate(years):
        x = left + idx * (bar_w + gap)
        y_cursor = chart_bottom
        for dom in domains:
            v = year_counts[year].get(dom, 0)
            h = (v / max_total) * chart_height if max_total else 0
            y_cursor -= h
            elements.append(
                f'<rect x="{x:.1f}" y="{y_cursor:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="{safe_color(dom)}" rx="6"/>'
            )
            if v > 0:
                elements.append(
                    f'<text x="{x + bar_w/2:.1f}" y="{y_cursor + h/2 + 4:.1f}" fill="#ecfeff" font-size="11" text-anchor="middle">{v}</text>'
                )

        elements.append(f'<text x="{x + bar_w/2:.1f}" y="{chart_bottom + 20}" fill="#dbeafe" font-size="12" text-anchor="middle">{year}</text>')

    # legend
    lx = width - 235
    ly = 24
    for i, dom in enumerate(domains):
        y = ly + i * 22
        label = dom.replace("_", " ")
        elements.append(f'<rect x="{lx}" y="{y}" width="14" height="14" fill="{safe_color(dom)}" rx="3"/>')
        elements.append(f'<text x="{lx + 22}" y="{y + 12}" fill="#c7d2fe" font-size="12">{label}</text>')

    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Distribución anual por dominio">{"".join(elements)}</svg>'


def build_rate_bars(rates: dict[str, float], title: str, label_suffix: str = "") -> str:
    blocks = [f'<h3>{title}</h3>', '<div class="bar-list">']
    for group, value in sorted(rates.items(), key=lambda x: x[1], reverse=True):
        pct = max(0, min(100, value * 100))
        blocks.append(
            """
            <div class="bar-item">
              <div class="bar-head">
                <span>{group}</span>
                <span>{pct:.1f}%{label_suffix}</span>
              </div>
              <div class="bar-track"><div class="bar-fill" style="width: {pct:.1f}%; background:{color};"></div></div>
            </div>
            """.format(group=group, pct=pct, label_suffix=label_suffix, color=safe_color(group))
        )
    blocks.append("</div>")
    return "".join(blocks)


def storytelling(rows: list[dict[str, str]], metrics: dict) -> str:
    total = len(rows)
    domains = Counter(r["dominio"] for r in rows)
    formats = Counter(r["formato"] for r in rows)
    top_format, top_format_count = formats.most_common(1)[0]
    bias = metrics["bias"]
    dp_region = bias["region"]["demographic_parity_difference"]
    dp_lang = bias["idioma"]["demographic_parity_difference"]
    acc = metrics["metrics"]["accuracy"]

    return f"""
    <section class=\"story\"> 
      <h2>Storytelling: del entusiasmo a la vigilancia ética</h2>
      <p><strong>Capítulo 1 — El mapa del movimiento:</strong> el dataset recoge <strong>{total} iniciativas</strong> entre 2024 y 2026. 
      Aunque ambas comunidades crecen, <strong>computación cuántica ({domains.get('computacion_cuantica', 0)})</strong> aparece con más señales públicas que 
      <strong>IA generativa ({domains.get('ia_generativa', 0)})</strong>.</p>

      <p><strong>Capítulo 2 — El formato que abre puertas:</strong> el formato más frecuente es 
      <strong>{top_format}</strong> ({top_format_count} registros), lo que sugiere una estrategia de acceso de bajo umbral: primero comunidad, luego especialización técnica.</p>

      <p><strong>Capítulo 3 — El modelo aprende, pero hay alertas:</strong> el clasificador base alcanza 
      <strong>{acc:.2%} de accuracy</strong> en test. Es prometedor como línea base, pero no definitivo por el tamaño muestral.</p>

      <p><strong>Capítulo 4 — El sesgo no siempre grita, a veces susurra:</strong> la diferencia de paridad demográfica es 
      <strong>{dp_region:.4f}</strong> por región y <strong>{dp_lang:.4f}</strong> por idioma. 
      En términos prácticos, la probabilidad de predecir “cuántica” no es homogénea entre subgrupos; por ello conviene ampliar datos y balancear muestra.</p>

      <p><strong>Próximo episodio:</strong> escalar el dataset (&gt;200 casos), normalizar taxonomías y reentrenar con validación cruzada para verificar que el desempeño y la equidad se sostienen fuera de esta muestra inicial.</p>
    </section>
    """


def main() -> None:
    rows = load_rows()
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    year_counts = yearly_domain_counts(rows)
    domain_counts = Counter(r["dominio"] for r in rows)
    region_counts = Counter(r["region"] for r in rows)
    language_counts = Counter(r["idioma"] for r in rows)

    region_pred_rates = {
        k: v["prediction_positive_rate"]
        for k, v in metrics["bias"]["region"]["group_rates"].items()
    }
    lang_pred_rates = {
        k: v["prediction_positive_rate"]
        for k, v in metrics["bias"]["idioma"]["group_rates"].items()
    }

    kpi_cards = f"""
      <div class=\"kpi-grid\">
        <div class=\"card\"><span>Registros</span><strong>{len(rows)}</strong></div>
        <div class=\"card\"><span>Accuracy (test)</span><strong>{metrics['metrics']['accuracy']:.2%}</strong></div>
        <div class=\"card\"><span>DP diff región</span><strong>{metrics['bias']['region']['demographic_parity_difference']:.4f}</strong></div>
        <div class=\"card\"><span>DP diff idioma</span><strong>{metrics['bias']['idioma']['demographic_parity_difference']:.4f}</strong></div>
      </div>
    """

    overview = f"""
    <section class=\"panel\">
      <h2>Panorama general</h2>
      <ul>
        <li><strong>Dominios:</strong> IA generativa ({domain_counts.get('ia_generativa', 0)}) vs Computación cuántica ({domain_counts.get('computacion_cuantica', 0)}).</li>
        <li><strong>Regiones:</strong> {', '.join(f'{k} ({v})' for k, v in region_counts.most_common())}.</li>
        <li><strong>Idiomas:</strong> {', '.join(f'{k} ({v})' for k, v in language_counts.most_common())}.</li>
      </ul>
      {build_stacked_bar_svg(year_counts)}
    </section>
    """

    fairness = f"""
    <section class=\"panel two-col\">
      <div>
        {build_rate_bars(region_pred_rates, 'Tasa de predicción positiva por región')}
      </div>
      <div>
        {build_rate_bars(lang_pred_rates, 'Tasa de predicción positiva por idioma')}
      </div>
    </section>
    """

    html = f"""<!doctype html>
<html lang=\"es\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Dashboard — Mujeres en IA Generativa y Computación Cuántica</title>
  <style>
    :root {{ color-scheme: dark; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Inter, Segoe UI, Roboto, Arial, sans-serif; background:#060b18; color:#e2e8f0; }}
    .wrap {{ max-width:1100px; margin:0 auto; padding:28px 20px 60px; }}
    h1 {{ margin:0 0 8px; font-size:1.9rem; }}
    .subtitle {{ margin:0 0 22px; color:#9fb0d9; }}
    .kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin-bottom:18px; }}
    .card {{ background:#0d1730; border:1px solid #1d2b4f; border-radius:12px; padding:14px; }}
    .card span {{ color:#9fb0d9; font-size:.9rem; display:block; }}
    .card strong {{ font-size:1.6rem; line-height:1.4; }}
    .panel {{ background:#0d1730; border:1px solid #1d2b4f; border-radius:12px; padding:16px; margin-top:14px; }}
    .two-col {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:16px; }}
    .panel h2, .panel h3 {{ margin-top:0; }}
    ul {{ margin:8px 0 14px; }}
    .bar-item {{ margin-bottom:10px; }}
    .bar-head {{ display:flex; justify-content:space-between; font-size:.9rem; margin-bottom:4px; color:#dbeafe; }}
    .bar-track {{ width:100%; height:12px; border-radius:999px; background:#1e293b; overflow:hidden; }}
    .bar-fill {{ height:100%; border-radius:999px; }}
    .story p {{ color:#dbeafe; line-height:1.55; }}
    .footer {{ color:#8aa0cf; font-size:.85rem; margin-top:16px; }}
  </style>
</head>
<body>
  <main class=\"wrap\">
    <h1>Dashboard de Divulgación STEM liderada por mujeres</h1>
    <p class=\"subtitle\">IA generativa vs computación cuántica (2024–2026) · métricas de desempeño y sesgo</p>
    {kpi_cards}
    {overview}
    {fairness}
    {storytelling(rows, metrics)}
    <p class=\"footer\">Fuente: data/women_divulgacion_ai_generativa_cuantica_2024_2026.csv + results/metricas_modelo_sesgo.json</p>
  </main>
</body>
</html>
"""

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard generado en {OUT_PATH}")


if __name__ == "__main__":
    main()
