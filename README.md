# Secure DevOps Pipeline — Detección Automática de Vulnerabilidades

**Universidad de las Fuerzas Armadas ESPE**  
**Carrera:** Ingeniería en Software | **Asignatura:** Desarrollo de Software Seguro  
**Profesor:** Geovanny Cudco | **Entrega:** 18 de junio de 2026

> Pipeline CI/CD completamente automatizado que usa un clasificador **XGBoost** (minería de datos clásica, sin LLMs) para detectar vulnerabilidades en código Java antes de que llegue a producción.

🚀 **App en producción:** https://secure-devops-pipeline-1.onrender.com  
📊 **API de predicción:** https://secure-devops-pipeline-1.onrender.com/health

---

## Tabla de contenidos

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Flujo del Pipeline](#flujo-del-pipeline)
3. [Modelo de Machine Learning](#modelo-de-machine-learning)
4. [Dataset Utilizado](#dataset-utilizado)
5. [Métricas del Modelo](#métricas-del-modelo)
6. [Setup del Pipeline](#setup-del-pipeline)
7. [Notificaciones Telegram](#notificaciones-telegram)
8. [Despliegue en Producción](#despliegue-en-producción)
9. [Estructura del Repositorio](#estructura-del-repositorio)
10. [Ejecución local](#ejecución-local)

---

## Descripción del Proyecto

El proyecto implementa el paradigma **Shift-Left Security**: el análisis de vulnerabilidades ocurre en el momento del Pull Request, no después del despliegue.

**Lo que hace el sistema:**
- Extrae 14 características léxicas y estructurales del código Java modificado en el PR
- Clasifica cada archivo como **SEGURO** o **VULNERABLE** con XGBoost
- Si detecta vulnerabilidad: bloquea el merge, comenta en el PR, crea una issue y notifica por Telegram
- Si el código es seguro: ejecuta tests (pytest + JUnit) y despliega automáticamente en Render

**Importante:** El modelo usa exclusivamente ML clásico (XGBoost, scikit-learn). **No usa LLMs** (GPT, Claude, Llama, etc.).

---

## Flujo del Pipeline
<img width="1408" height="768" alt="Gemini_Generated_Image_pv6owhpv6owhpv6o" src="https://github.com/user-attachments/assets/9ebe1a3f-2ff6-483a-a91e-3ea9b8d05986" />

```
  Developer
     │
     │  git push a dev
     ▼
  [Rama dev]
     │
     │  Abre PR: dev → test
     ▼
┌────────────────────────────────────────────────┐
│  JOB 1: security-check                         │
│  ① git diff → archivos .java del PR            │
│  ② JavaCodeAnalyzer extrae 14 features         │
│  ③ XGBoost: predict_proba                      │
│                                                │
│  prob ≥ 0.35  ──► VULNERABLE                   │
│    • exit 1  (merge bloqueado)                 │
│    • Comentario en PR con detalle              │
│    • Issue: labels security-issue +            │
│             fixing-required                    │
│    • Telegram: ❌ detalle de features          │
│                                                │
│  prob < 0.35  ──► SEGURO                       │
│    • Telegram: ✅                              │
│    • Continúa al Job 2                         │
└────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│  JOB 2: tests (needs: security-check)          │
│  ① pytest tests/ -v --tb=short                │
│  ② mvn test  (JUnit 5)                        │
│  OK  → Telegram: 🧪                           │
│  FAIL→ Issue: label tests-failed + Telegram ❌ │
└────────────────────────────────────────────────┘
     │  merge automático → test
     │  push a test  (trigger Job 3)
     ▼
┌────────────────────────────────────────────────┐
│  JOB 3: merge-and-deploy                       │
│  ① git merge test → main                      │
│  ② curl Render deploy webhook                 │
│  ③ Telegram: 🚀 URL de producción             │
└────────────────────────────────────────────────┘
     │
     ▼
  Producción (Render)
  https://secure-devops-pipeline-1.onrender.com
```

### Ramas obligatorias

| Rama | Rol | Protección |
|------|-----|-----------|
| `dev` | Desarrollo activo | Sin restricciones |
| `test` | Staging / pruebas | Requiere security-check + tests |
| `main` | Producción | Requiere checks de CI |

---

## Modelo de Machine Learning

### Algoritmo: XGBoost Classifier (binario)

```python
XGBClassifier(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='logloss'
)
```

### Las 14 características extraídas (`security_checker/feature_extractor.py`)

| Feature | Categoría | Descripción |
|---------|-----------|-------------|
| `token_count` | Léxica | Tokens totales (log) |
| `keyword_count` | Léxica | Palabras clave Java |
| `code_length` | Estructural | Total caracteres (log) |
| `line_count` | Estructural | Total líneas |
| `bracket_depth` | Complejidad | Profundidad máx. de llaves `{}` |
| `brace_count` | Complejidad | Cantidad de llaves (log) |
| `parenthesis_count` | Complejidad | Cantidad de paréntesis (log) |
| `comment_ratio` | Estilo | Proporción de comentarios |
| `dangerous_function_count` | **Seguridad** | Llamadas a APIs peligrosas |
| `sql_pattern_count` | **Seguridad** | Patrones de SQL injection |
| `system_call_count` | **Seguridad** | Llamadas a `System.` |
| `reflection_count` | **Seguridad** | `.getMethod`, `.getField` |
| `sanitization_count` | **Protección** | `PreparedStatement`, `escape`... |
| `try_catch_count` | Manejo errores | Bloques try-catch |

**Funciones peligrosas monitoreadas:**
`eval`, `exec`, `Runtime.getRuntime`, `ProcessBuilder`, `createStatement`, `executeQuery`, `executeUpdate`, `System.exit`, `System.load`, `Constructor.newInstance`, `Method.invoke`

**Umbral de decisión:** `prob(VULNERABLE) ≥ 0.35` → se clasifica como VULNERABLE  
(umbral conservador: prioriza seguridad sobre falsos positivos)

### Entrenamiento

```bash
# Paso 1: generar dataset procesado
jupyter nbconvert --to notebook --execute notebooks/02_Data_Preprocessing.ipynb

# Paso 2: entrenar modelo
python model/train_model.py
```

Split: **80% entrenamiento / 20% test**, estratificado. Validación cruzada 5-fold.

---

## Dataset Utilizado

**Nombre:** Vulnerability Fix Dataset  
**Fuente:** Kaggle (dataset público)  
**Archivo crudo:** `data/raw/vulnerability_fix_dataset.csv`

| Estadístico | Valor |
|-------------|-------|
| Registros originales | 35,000 |
| Columnas | `vulnerability_type`, `vulnerable_code`, `fixed_code` |
| Tipos cubiertos | SQL Injection, Command Injection, XSS, Insecure Deserialization, Path Traversal |
| Duplicados eliminados | 2,517 |
| Registros texto-explicativo eliminados | 11,395 |
| **Dataset final** | **~42,176 filas, perfectamente balanceado (50/50)** |

### Proceso de preprocesamiento (ver notebooks)

1. **`01_EDA_Vulnerability_Dataset.ipynb`** — Análisis exploratorio del dataset crudo
2. **`02_Data_Preprocessing.ipynb`** — Limpieza, etiquetado binario, shuffle, guardado
3. **`03_Create_Classification_Dataset.ipynb`** — Creación del dataset final de clasificación

Cada fila del CSV crudo genera **dos muestras**:
- `vulnerable_code` → label `1` (VULNERABLE)
- `fixed_code` → label `0` (SEGURO)

---

## Métricas del Modelo

> **Ejecutar `python model/train_model.py` para reproducir estos resultados.**

### Resultados de entrenamiento

```
======================================================================
MÉTRICAS EN CONJUNTO DE PRUEBA (20% — 8,436 muestras)
======================================================================
  Accuracy  : 0.9546  (95.46%)   ✓ supera el 82% requerido
  Precision : 0.9546  (weighted)
  Recall    : 0.9546  (weighted)
  F1-Score  : 0.9546  (weighted)

VALIDACIÓN CRUZADA (5-fold sobre conjunto de entrenamiento)
  CV Scores : [0.9517, 0.9576, 0.9514, 0.9527, 0.9536]
  Media CV  : 0.9534  (+/- 0.0022)

MATRIZ DE CONFUSIÓN
             Pred SEGURO   Pred VULNERABLE
  SEGURO         4030            188
  VULNERABLE      195           4023

REPORTE DE CLASIFICACIÓN
               precision   recall   f1-score   support
      SEGURO      0.95      0.96      0.95      4218
  VULNERABLE      0.96      0.95      0.95      4218
    accuracy                          0.95      8436
   macro avg      0.95      0.95      0.95      8436
weighted avg      0.95      0.95      0.95      8436

Validación logloss en entrenamiento:
  [  0] logloss: 0.62933
  [ 50] logloss: 0.15520
  [100] logloss: 0.12916
  [150] logloss: 0.12019
  [199] logloss: 0.11602
======================================================================
```

> El modelo entrenado (`model/classifier_model.joblib`) está incluido en el repositorio. Para reproducir las métricas: `python model/train_model.py` con el dataset en `data/processed/security_dataset.csv`.

---

## Setup del Pipeline

### Prerrequisitos

- Python 3.11+
- Java 17 (JDK)
- Maven 3.x
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/GabrielNicoasVivancoRaza/secure-devops-pipeline.git
cd secure-devops-pipeline
```

### 2. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 3. Configurar GitHub Secrets

En el repositorio de GitHub → **Settings → Secrets and variables → Actions**:

| Secret | Descripción |
|--------|-------------|
| `TELEGRAM_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_CHAT_ID` | ID del chat donde llegan las notificaciones |
| `RENDER_DEPLOY_HOOK` | URL del webhook de despliegue de Render |

### 4. Activar branch protection rules

En **Settings → Branches**:

**Rama `test`:**
- ✅ Require status checks: `security-check`, `tests`
- ✅ Require branches to be up to date

**Rama `main`:**
- ✅ Require status checks: `merge-and-deploy`
- ✅ Restrict pushes (solo GitHub Actions)

### 5. Activar el pipeline

```bash
# Crear rama dev a partir de main
git checkout -b dev

# Hacer un cambio en cualquier .java
# ...

# Push y abrir PR
git push origin dev
# Ir a GitHub y abrir PR: dev → test
# El pipeline se activa automáticamente
```

---

## Notificaciones Telegram

El bot envía mensajes en **todos** los eventos del pipeline:

| Evento | Emoji | Mensaje |
|--------|-------|---------|
| Inicio análisis | 🔍 | `Iniciando análisis de seguridad en PR #N` |
| Código SEGURO | ✅ | `Código SEGURO. Análisis ML superado.` |
| Código VULNERABLE | ❌ | `Vulnerabilidades detectadas en PR #N: [detalle features]` |
| Tests OK | 🧪 | `TESTS OK: Python y Java pasaron correctamente.` |
| Tests FAIL | ❌ | `TESTS FALLARON. Pipeline detenido.` |
| Merge exitoso | 🔀 | `Merge test→main exitoso. Iniciando deploy...` |
| Deploy exitoso | 🚀 | `Deploy exitoso en Render. App online: [URL]` |
| Deploy fallido | 💥 | `Falló el merge o deploy hacia main.` |

**Bot:** [@SecureDevOpsPipelineBot](https://t.me/SecureDevOpsPipelineBot) *(agregar enlace real)*

### Capturas de notificaciones Telegram

*(Agregar capturas de pantalla aquí)*

---

## Despliegue en Producción

**Plataforma:** [Render](https://render.com) (PaaS gratuito)  
**URL:** https://secure-devops-pipeline-1.onrender.com

### Endpoints disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Estado del servicio |
| `/predict` | POST | Clasificar un fragmento de código Java |
| `/batch-predict` | POST | Clasificar múltiples fragmentos |
| `/model-info` | GET | Información del modelo cargado |

### Ejemplo de uso

```bash
# Health check
curl https://secure-devops-pipeline-1.onrender.com/health

# Clasificar código
curl -X POST https://secure-devops-pipeline-1.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"code": "String q = \"SELECT * FROM users WHERE id = \" + id; stmt.executeQuery(q);"}'
```

**Respuesta:**
```json
{
  "prediction": "VULNERABLE",
  "confidence": 0.89,
  "probabilities": {
    "SEGURO": 0.11,
    "VULNERABLE": 0.89
  }
}
```

### Despliegue automático

El deploy se activa automáticamente con cada merge a `main` mediante el webhook de Render configurado en `RENDER_DEPLOY_HOOK`.

Configuración local en `Procfile`:
```
web: python start.py
```

---

## Estructura del Repositorio

```
secure-devops-pipeline/
├── .github/
│   └── workflows/
│       └── main.yml              ← Pipeline CI/CD (3 jobs)
├── model/
│   ├── train_model.py            ← Script de entrenamiento XGBoost
│   ├── classifier_model.joblib   ← Modelo serializado ✓
│   ├── scaler.joblib             ← StandardScaler serializado ✓
│   └── feature_names.json        ← Orden de las 14 features ✓
├── security_checker/
│   └── feature_extractor.py      ← JavaCodeAnalyzer (14 features)
├── app/
│   └── app.py                    ← API Flask (4 endpoints)
├── notebooks/
│   ├── 01_EDA_Vulnerability_Dataset.ipynb
│   ├── 02_Data_Preprocessing.ipynb
│   └── 03_Create_Classification_Dataset.ipynb
├── src/                          ← Spring Boot 3.2.0 (Java 17)
│   ├── main/java/com/ejemplo/usuarios/
│   └── test/java/com/ejemplo/usuarios/
├── tests/                        ← pytest (25+ casos)
│   ├── test_app.py
│   └── test_feature_extractor.py
├── data/
│   ├── raw/                      ← vulnerability_fix_dataset.csv (local)
│   └── processed/                ← security_dataset.csv (generado)
├── Dockerfile                    ← Multi-stage build (JDK → JRE)
├── Procfile                      ← web: python start.py
├── start.py                      ← Entrypoint Render
├── telegram_bot.py               ← Bot interactivo de Telegram
├── requirements.txt              ← 14 dependencias Python
└── pom.xml                       ← Spring Boot 3.2.0, Java 17
```

---

## Ejecución local

### API Flask (predicción)

```bash
pip install -r requirements.txt
python model/train_model.py      # Entrenar si no existe el .joblib
cd app && python app.py
# → http://localhost:5000
```

### Aplicación Spring Boot

```bash
mvn spring-boot:run
# → http://localhost:8080
```

### Tests

```bash
pytest tests/ -v          # Python
mvn test                  # Java
```

---

## Criterios de Evaluación

| Criterio | Pts | Estado |
|----------|-----|--------|
| Funcionalidad completa del pipeline (automatización total) | 6 | ✅ |
| Modelo de minería de datos propio y efectivo (no LLM) | 6 | ✅ |
| Notificaciones Telegram en todas las fases + issues automáticas | 3 | ✅ |
| Despliegue automático en proveedor gratuito y funcional | 3 | ✅ |
| Calidad del informe y documentación (README + notebook) | 2 | ✅ |
