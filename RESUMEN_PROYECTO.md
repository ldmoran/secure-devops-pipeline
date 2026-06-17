# Secure DevOps Pipeline — Resumen Técnico del Proyecto

**Universidad de las Fuerzas Armadas ESPE**  
**Asignatura:** Desarrollo de Software Seguro  
**Profesor:** Geovanny Cudco  
**Entrega:** 18 de junio de 2026  

---

## ¿Qué es este proyecto?

Un pipeline CI/CD completamente automatizado que integra un modelo de Machine Learning clásico (XGBoost) para detectar vulnerabilidades en código Java antes de permitir que llegue a producción. El flujo va de `dev` → `test` → `main`, y en ningún punto interviene un humano para aprobar el merge.

**Repositorio:** GitHub  
**Aplicación desplegada:** https://secure-devops-pipeline-1.onrender.com  

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Modelo ML | XGBoost 3.1.3 (clasificador binario) |
| Extracción de features | Python 3.11, regex, análisis léxico |
| API de predicción | Flask 3.0.0 + Gunicorn |
| Aplicación de demostración | Spring Boot 3.2.0, Java 17 |
| CI/CD | GitHub Actions |
| Despliegue | Render (PaaS gratuito) |
| Contenedores | Docker (multi-stage, eclipse-temurin:17) |
| Notificaciones | Telegram Bot API |
| Tests Python | pytest 7.4.3 |
| Tests Java | JUnit 5 + Maven |
| Serialización del modelo | joblib 1.5.1 |
| Normalización | scikit-learn StandardScaler |

---

## Modelo de Machine Learning

### Algoritmo: XGBoost Classifier (binario)

```
VULNERABLE = 1  /  SEGURO = 0
Umbral de decisión: probabilidad ≥ 0.35 → VULNERABLE
```

**Hiperparámetros de entrenamiento:**
- `n_estimators = 200`
- `max_depth = 8`
- `learning_rate = 0.1`
- `subsample = 0.8`
- `colsample_bytree = 0.8`
- `eval_metric = logloss`
- Split 80/20 estratificado, validación cruzada 5-fold

**Archivos del modelo:**
- `model/classifier_model.joblib` — modelo serializado
- `model/scaler.joblib` — StandardScaler ajustado al set de entrenamiento
- `model/feature_names.json` — orden exacto de las 14 features

### Las 14 features extraídas de código Java

| Feature | Descripción |
|---------|-------------|
| `brace_count` | Número de llaves `{ }` (log-transformado) |
| `bracket_depth` | Profundidad máxima de anidamiento de llaves |
| `code_length` | Total de caracteres (log-transformado) |
| `comment_ratio` | Proporción de caracteres en comentarios |
| `dangerous_function_count` | Llamadas a APIs peligrosas |
| `keyword_count` | Ocurrencias de palabras clave Java |
| `line_count` | Total de líneas |
| `parenthesis_count` | Número de paréntesis `( )` (log-transformado) |
| `reflection_count` | Usos de `.getMethod` / `.getField` |
| `sanitization_count` | Mecanismos de sanitización presentes |
| `sql_pattern_count` | Patrones de posible SQL injection |
| `system_call_count` | Llamadas a `System.` |
| `token_count` | Total de tokens léxicos (log-transformado) |
| `try_catch_count` | Bloques try-catch |

**Funciones peligrosas monitoreadas:**
`eval`, `exec`, `Runtime.getRuntime`, `ProcessBuilder`, `createStatement`, `executeQuery`, `executeUpdate`, `System.exit`, `System.load`, `System.loadLibrary`, `Constructor.newInstance`, `Method.invoke`

**Patrones de sanitización detectados:**
`PreparedStatement`, `parameterized`, `sanitize`, `escape`, `validate`, `whitelist`, `htmlEncode`, `urlEncode`

### Dataset

- **Fuente:** Dataset público de vulnerabilidades (Vulnerability Fix Dataset)
- **Tamaño original:** 35,000 registros con pares `(vulnerable_code, fixed_code)`
- **Tipos de vulnerabilidad:** SQL Injection, Command Injection, XSS, Insecure Deserialization, Path Traversal
- **Notebooks de análisis:** `notebooks/01_EDA_Vulnerability_Dataset.ipynb`, `02_Data_Preprocessing.ipynb`, `03_Create_Classification_Dataset.ipynb`
- **Dataset procesado:** `data/processed/security_dataset.csv` (columnas `code`, `label`)

---

## Pipeline CI/CD — Flujo completo

```
Developer push a dev
        │
        ▼
  PR: dev → test          ◄── trigger del pipeline
        │
        ▼
┌─────────────────────────────────────────┐
│  JOB 1: security-check                  │
│  1. git diff → archivos .java del PR    │
│  2. Extraer 14 features por archivo     │
│  3. XGBoost predict_proba               │
│  4a. prob ≥ 0.35 → VULNERABLE           │
│       • Bloquear merge (exit 1)         │
│       • Comentario detallado en el PR   │
│       • Issue con label security-issue  │
│       • Notificación Telegram ❌        │
│  4b. prob < 0.35 → SEGURO              │
│       • Notificación Telegram ✅        │
│       • Continúa al job 2               │
└─────────────────────────────────────────┘
        │ (solo si SEGURO)
        ▼
┌─────────────────────────────────────────┐
│  JOB 2: tests (needs: security-check)   │
│  1. pytest tests/ -v --tb=short         │
│  2. mvn test (JUnit 5)                  │
│  OK → Notificación Telegram 🧪          │
│  FAIL → Issue label tests-failed + ❌   │
└─────────────────────────────────────────┘
        │ (solo si tests pasan → merge a test)
        ▼
┌─────────────────────────────────────────┐
│  JOB 3: merge-and-deploy                │
│  Trigger: push a rama test              │
│  1. git merge test → main               │
│  2. git push origin main                │
│  3. curl Render deploy webhook          │
│  4. Notificación Telegram 🚀            │
└─────────────────────────────────────────┘
        │
        ▼
   Producción en Render
```

**Workflow:** `.github/workflows/main.yml`

---

## Notificaciones Telegram

El bot envía mensajes en **todos** los eventos del pipeline:

| Evento | Mensaje |
|--------|---------|
| Inicio análisis | `🔍 Iniciando análisis de seguridad en PR #N` |
| Código SEGURO | `✅ Código SEGURO. Análisis ML superado.` |
| Código VULNERABLE | `❌ Vulnerabilidades detectadas en PR #N: [detalle]` |
| Tests OK | `🧪 TESTS OK: Python y Java pasaron correctamente.` |
| Tests FAIL | `❌ TESTS FALLARON. Pipeline detenido.` |
| Merge exitoso | `🔀 Merge test→main exitoso. Iniciando deploy...` |
| Deploy exitoso | `🚀 Deploy exitoso en Render. App online: [URL]` |
| Deploy fallido | `💥 Falló el merge o deploy hacia main.` |

Credenciales en **GitHub Secrets**: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `RENDER_DEPLOY_HOOK`

---

## Aplicación de demostración (Spring Boot)

Una API REST CRUD de usuarios que sirve como código objetivo del análisis. Está desplegada en Render junto a la API Flask.

**Endpoints Java:**
- `GET /usuarios` — listar todos
- `GET /usuarios/{id}` — obtener por ID
- `POST /usuarios` — crear (valida `@NotBlank`, `@Email`)
- `PUT /usuarios/{id}` — actualizar
- `DELETE /usuarios/{id}` — eliminar
- `GET /health` — health check

**Almacenamiento:** en memoria (HashMap + AtomicLong), pre-cargado con 2 usuarios de muestra.

---

## API Flask de predicción

**Base URL:** `https://secure-devops-pipeline-1.onrender.com`

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Estado del servicio y si el modelo está cargado |
| `/predict` | POST | Clasificar un fragmento de código Java |
| `/batch-predict` | POST | Clasificar múltiples fragmentos a la vez |
| `/model-info` | GET | Metadata del modelo (tipo, features, clases) |

**Ejemplo de uso:**
```bash
curl -X POST https://secure-devops-pipeline-1.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"code": "String query = \"SELECT * FROM users WHERE id = \" + userId;"}'
```

**Respuesta:**
```json
{
  "prediction": "VULNERABLE",
  "confidence": 0.87,
  "probabilities": {"SEGURO": 0.13, "VULNERABLE": 0.87}
}
```

---

## Tests

### Python (pytest)
- `tests/test_app.py` — importación de Flask, endpoint `/health`, carga del modelo
- `tests/test_feature_extractor.py` — 18 casos: código vacío, detección de funciones peligrosas, SQL injection, sanitización, manejo de excepciones, profundidad de llaves, conversión a array, presencia de las 14 features

### Java (JUnit 5 + Maven)
- `src/test/java/.../UsuarioServiceTest.java` — 8 casos: CRUD completo, IDs inexistentes, integridad de datos

---

## Estructura de archivos clave

```
secure-devops-pipeline/
├── .github/workflows/main.yml     ← definición completa del pipeline
├── model/
│   ├── train_model.py             ← script de entrenamiento
│   ├── classifier_model.joblib    ← modelo XGBoost serializado
│   ├── scaler.joblib              ← StandardScaler serializado
│   └── feature_names.json         ← lista ordenada de features
├── security_checker/
│   └── feature_extractor.py      ← JavaCodeAnalyzer (14 features)
├── app/
│   └── app.py                    ← API Flask con endpoints de predicción
├── notebooks/
│   ├── 01_EDA_Vulnerability_Dataset.ipynb
│   ├── 02_Data_Preprocessing.ipynb
│   └── 03_Create_Classification_Dataset.ipynb
├── src/                           ← Spring Boot (código analizado)
├── tests/                         ← pytest
├── Dockerfile                     ← multi-stage build
├── Procfile                       ← start.py → gunicorn
├── start.py                       ← entrypoint en Render (auto-entrena si falta modelo)
├── telegram_bot.py                ← bot para predicción manual por Telegram
├── requirements.txt               ← 14 dependencias Python
└── pom.xml                        ← Spring Boot 3.2.0, Java 17
```

---

## Cómo correr el proyecto localmente

### 1. API Flask (modelo de predicción)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Entrenar el modelo (requiere data/processed/security_dataset.csv)
python model/train_model.py

# Levantar la API
cd app && python app.py
# → http://localhost:5000
```

### 2. Aplicación Spring Boot

```bash
# Requiere Java 17 y Maven
mvn spring-boot:run
# → http://localhost:8080
```

### 3. Ejecutar tests

```bash
# Python
pytest tests/ -v

# Java
mvn test
```

### 4. Activar el pipeline completo

```bash
# Crear rama dev, hacer cambio en un .java, abrir PR hacia test
git checkout -b dev
# ... editar código ...
git push origin dev
# Abrir PR: dev → test en GitHub
# El pipeline se activa automáticamente
```

---

## Cumplimiento de requisitos del proyecto

| Requisito | Estado |
|-----------|--------|
| Modelo ML clásico propio (no LLM) | ✅ XGBoost entrenado |
| Archivo `.joblib` entregado | ✅ `model/classifier_model.joblib` |
| Dataset público | ✅ Vulnerability Fix Dataset (35K registros) |
| Features mínimas (tokens, AST, funciones peligrosas, sanitización) | ✅ 14 features |
| Accuracy ≥ 82% en validación cruzada | ✅ Reportado en entrenamiento con 5-fold CV |
| Telegram Bot propio con token en Secrets | ✅ |
| Despliegue real y funcional | ✅ Render, online |
| Branch protection en `test` y `main` | ✅ GitHub Actions required checks |
| PR bloqueado si VULNERABLE | ✅ `exit 1` en el job |
| Comentario en PR con detalle | ✅ `github-script` |
| Issue automática al detectar vulnerabilidad | ✅ Labels `security-issue`, `fixing-required` |
| Issue automática si fallan tests | ✅ Label `tests-failed` |
| Merge automático `test → main` | ✅ Job `merge-and-deploy` |
| Deploy automático en proveedor gratuito | ✅ Render webhook |
| Notificaciones en todas las fases | ✅ 8 eventos cubiertos |
| Notebooks de EDA y preprocesamiento | ✅ 3 notebooks |
| Informe técnico en LaTeX | ✅ `informe_tecnico.tex` |
