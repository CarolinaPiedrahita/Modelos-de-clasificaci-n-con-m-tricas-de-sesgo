# Revisión exhaustiva (2024–2026): divulgación científica liderada por mujeres en IA generativa y computación cuántica

**Fecha de corte:** 9 de abril de 2026.

## 1) Alcance y objetivo

Esta revisión sintetiza iniciativas públicas de divulgación científica (conferencias, talleres, webinars, comunidades, mentorías y reportes) lideradas por mujeres o redes de mujeres en dos dominios:

- **IA generativa**
- **Computación cuántica**

El objetivo operativo es construir una base curada para entrenar un **modelo de clasificación** y auditarlo con **métricas de sesgo**.

## 2) Corpus curado

Se consolidó un dataset estructurado en:

- `data/women_divulgacion_ai_generativa_cuantica_2024_2026.csv`

Con **26 registros** fechados entre 2024 y 2026 (incluyendo continuidad anual de programas).

### Distribución por dominio

- IA generativa: 10 registros
- Computación cuántica: 16 registros

### Campos incluidos

- fecha
- iniciativa
- lideres
- dominio
- formato
- region
- idioma
- descripcion
- fuente

## 3) Hallazgos de divulgación científica (síntesis)

## 3.1 IA generativa

Patrones observados:

1. **Institucionalización ética**: UNESCO consolida el eje Women4Ethical AI con foco en sesgos de género en LLM y gobernanza.
2. **Divulgación multi-formato**: reportes, conferencias, comunidades y webinars.
3. **Tránsito academia-industria**: Women in AI y WiCV conectan mentoría, carrera profesional y comunicación pública de investigación.

## 3.2 Computación cuántica

Patrones observados:

1. **Ecosistema comunitario global**: Girls in Quantum, SheQuantum, Women in Quantum.
2. **Canales de entrada accesibles**: podcasts, hackatones, webinars para estudiantes y profesionales en transición.
3. **Consolidación anual**: talleres y escuelas que repiten edición (2024→2025→2026), señal de madurez en divulgación.

## 3.3 Señales transversales (IA + cuántica)

- Alta presencia de **formatos de bajo umbral de entrada** (webinars, comunidad, mentoría).
- Fuerte uso de **narrativas de trayectoria** (career pathways) para captar talento femenino.
- Persistencia de brechas regionales/idioma: predominio del inglés y mayor actividad reportada en redes globales + Europa/EE.UU.

## 4) Modelo de clasificación con métricas de sesgo

Se implementó un baseline en:

- `src/modelo_clasificacion_sesgo.py`

### Diseño del modelo

- Tipo: **Naive Bayes multinomial** (implementación propia con librería estándar, sin dependencias externas).
- Objetivo: clasificar iniciativas en `ia_generativa` vs `computacion_cuantica`.
- Features: texto combinado de iniciativa, líderes, formato, región, idioma y descripción.
- Split: 70% entrenamiento / 30% prueba (semilla fija 42).

### Métricas evaluadas

- Accuracy
- Precision/Recall/F1 para clase positiva (`computacion_cuantica`)
- Matriz de confusión
- **Bias metrics**:
  - Demographic Parity Difference (por `region`, `idioma`)
  - Equal Opportunity Difference (por `region`, `idioma`)

Resultados exportados en:

- `results/metricas_modelo_sesgo.json`

## 5) Limitaciones (importantes para interpretar el modelo)

1. Dataset pequeño (n=26) y curado manualmente.
2. Posible sesgo de disponibilidad: eventos con mayor presencia digital quedan sobrerrepresentados.
3. Algunas iniciativas son “programas continuos” y no un evento único.
4. “Exhaustiva” se interpreta aquí como **cobertura amplia y trazable** al corte temporal, no censo universal.

## 6) Recomendaciones para versión 2

- Aumentar muestra (n>200) con scraping/ETL reproducible por fuentes oficiales.
- Etiquetado doble ciego para la variable `dominio` y taxonomías más finas (educación, policy, investigación, industria).
- Añadir atributos de equidad mejor definidos (p. ej. región normalizada por ONU, idioma principal, nivel de acceso).
- Evaluar modelos robustos (logistic regression / transformer ligero) y calibración.

## 7) Fuentes base utilizadas para la curación

- UNESCO (Women4Ethical AI, conferencia 2024, estudio de sesgo en LLM).
- Women in AI (eventos y programas de comunidad/divulgación).
- WiCV @ CVPR (reportes 2024 y 2025).
- Girls in Quantum (news y actividades globales).
- IAPS – Women in Quantum.
- NCWIT (webinar Step into Quantum).
- Women for Quantum Workshop (UIB).
- SheQuantum.
- WISER/Womanium.

> Nota metodológica: en el CSV cada registro incluye su URL fuente para auditoría.
