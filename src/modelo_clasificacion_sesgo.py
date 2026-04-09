#!/usr/bin/env python3
"""Modelo base para clasificar iniciativas de divulgación en IA generativa vs computación cuántica.

Sin dependencias externas: usa Naive Bayes multinomial implementado con librerías estándar.
También calcula métricas de sesgo por subgrupos (región e idioma).
"""

from __future__ import annotations

import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

DATA_PATH = Path('data/women_divulgacion_ai_generativa_cuantica_2024_2026.csv')
OUT_PATH = Path('results/metricas_modelo_sesgo.json')

RANDOM_SEED = 42
POSITIVE_CLASS = 'computacion_cuantica'


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ0-9_]+", text.lower())


def build_text(row: dict[str, str]) -> str:
    fields = [
        row['iniciativa'],
        row['lideres'],
        row['formato'],
        row['region'],
        row['idioma'],
        row['descripcion'],
    ]
    return ' '.join(fields)


def train_nb(rows: list[dict[str, str]]):
    class_counts = Counter()
    token_counts = defaultdict(Counter)
    total_tokens = Counter()
    vocab = set()

    for row in rows:
        label = row['dominio']
        class_counts[label] += 1
        for tok in tokenize(build_text(row)):
            token_counts[label][tok] += 1
            total_tokens[label] += 1
            vocab.add(tok)

    priors = {
        c: math.log(class_counts[c] / len(rows))
        for c in class_counts
    }
    return priors, token_counts, total_tokens, vocab


def predict(row, model):
    priors, token_counts, total_tokens, vocab = model
    vocab_size = max(len(vocab), 1)

    scores = {}
    tokens = tokenize(build_text(row))
    for c, prior in priors.items():
        score = prior
        denom = total_tokens[c] + vocab_size
        for t in tokens:
            num = token_counts[c][t] + 1  # Laplace
            score += math.log(num / denom)
        scores[c] = score

    return max(scores, key=scores.get), scores


def confusion(y_true: list[str], y_pred: list[str], positive: str):
    tp = fp = tn = fn = 0
    for yt, yp in zip(y_true, y_pred):
        if yt == positive and yp == positive:
            tp += 1
        elif yt != positive and yp == positive:
            fp += 1
        elif yt != positive and yp != positive:
            tn += 1
        else:
            fn += 1
    return tp, fp, tn, fn


def classification_metrics(y_true, y_pred, positive=POSITIVE_CLASS):
    tp, fp, tn, fn = confusion(y_true, y_pred, positive)
    acc = (tp + tn) / max(len(y_true), 1)
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    f1 = (2 * prec * rec) / max(prec + rec, 1e-12)
    return {
        'accuracy': round(acc, 4),
        'precision_positive': round(prec, 4),
        'recall_positive': round(rec, 4),
        'f1_positive': round(f1, 4),
        'confusion_matrix': {'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn},
    }


def group_rates(rows, y_true, y_pred, attribute, positive=POSITIVE_CLASS):
    by_group = defaultdict(list)
    for row, yt, yp in zip(rows, y_true, y_pred):
        by_group[row[attribute]].append((yt, yp))

    rates = {}
    for group, pairs in by_group.items():
        pred_pos = sum(1 for _, yp in pairs if yp == positive)
        true_pos = sum(1 for yt, _ in pairs if yt == positive)
        tp = sum(1 for yt, yp in pairs if yt == positive and yp == positive)

        positive_rate = pred_pos / len(pairs)
        tpr = tp / true_pos if true_pos else None
        rates[group] = {
            'n': len(pairs),
            'prediction_positive_rate': round(positive_rate, 4),
            'true_positive_rate': None if tpr is None else round(tpr, 4),
        }

    valid_tpr = [v['true_positive_rate'] for v in rates.values() if v['true_positive_rate'] is not None]
    pred_rates = [v['prediction_positive_rate'] for v in rates.values()]

    dp_diff = (max(pred_rates) - min(pred_rates)) if pred_rates else 0.0
    eo_diff = (max(valid_tpr) - min(valid_tpr)) if len(valid_tpr) >= 2 else None

    return rates, round(dp_diff, 4), None if eo_diff is None else round(eo_diff, 4)


def main():
    with DATA_PATH.open(encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    random.Random(RANDOM_SEED).shuffle(rows)
    split_idx = int(0.7 * len(rows))
    train_rows = rows[:split_idx]
    test_rows = rows[split_idx:]

    model = train_nb(train_rows)

    y_true, y_pred = [], []
    for row in test_rows:
        pred, _ = predict(row, model)
        y_true.append(row['dominio'])
        y_pred.append(pred)

    overall = classification_metrics(y_true, y_pred)
    by_region, dp_region, eo_region = group_rates(test_rows, y_true, y_pred, 'region')
    by_idioma, dp_idioma, eo_idioma = group_rates(test_rows, y_true, y_pred, 'idioma')

    output = {
        'data': {
            'rows_total': len(rows),
            'rows_train': len(train_rows),
            'rows_test': len(test_rows),
            'target_labels': sorted(list({r['dominio'] for r in rows})),
            'positive_class': POSITIVE_CLASS,
        },
        'metrics': overall,
        'bias': {
            'region': {
                'group_rates': by_region,
                'demographic_parity_difference': dp_region,
                'equal_opportunity_difference': eo_region,
            },
            'idioma': {
                'group_rates': by_idioma,
                'demographic_parity_difference': dp_idioma,
                'equal_opportunity_difference': eo_idioma,
            },
        },
        'notes': [
            'Dataset pequeño y curado manualmente; usar solo como línea base demostrativa.',
            'Las métricas de sesgo dependen del desbalance de subgrupos y tamaño muestral.',
        ],
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')

    print('Métricas generales:', json.dumps(overall, ensure_ascii=False))
    print('Sesgo por región (DP diff):', dp_region, '| EO diff:', eo_region)
    print('Sesgo por idioma (DP diff):', dp_idioma, '| EO diff:', eo_idioma)
    print(f'Reporte guardado en {OUT_PATH}')


if __name__ == '__main__':
    main()
