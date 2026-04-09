# Modelos de clasificación con métricas de sesgo

Este repositorio contiene una revisión y una línea base reproducible para:

1. Analizar **divulgación científica liderada por mujeres** en:
   - IA generativa
   - Computación cuántica
2. Entrenar un **modelo de clasificación** por dominio.
3. Medir sesgo por subgrupos con métricas de equidad.

## Estructura

- `data/women_divulgacion_ai_generativa_cuantica_2024_2026.csv`  
  Dataset curado (2024–2026) con iniciativas, liderazgo, formato, región, idioma y fuente.

- `src/modelo_clasificacion_sesgo.py`  
  Implementación de Naive Bayes (sin dependencias externas) + métricas de desempeño y sesgo.

- `reports/revision_exhaustiva_mujeres_ia_generativa_cuantica.md`  
  Revisión narrativa y hallazgos.

- `results/metricas_modelo_sesgo.json`  
  Salida del modelo con métricas globales y por subgrupos.

## Cómo ejecutar

```bash
python src/modelo_clasificacion_sesgo.py
```

## Métricas reportadas

- Accuracy
- Precision / Recall / F1 (clase positiva: `computacion_cuantica`)
- Matriz de confusión
- Demographic Parity Difference (por región e idioma)
- Equal Opportunity Difference (por región e idioma)

## Nota de uso responsable

El dataset es pequeño y curado manualmente; los resultados deben interpretarse como **línea base exploratoria** y no como evaluación definitiva.

## Dashboard narrativo

Genera un dashboard HTML con gráficos y storytelling:

```bash
python src/generar_dashboard_storytelling.py
```

Archivo de salida:

- `reports/dashboard_storytelling.html`
