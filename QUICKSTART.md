# 🚀 GUÍA RÁPIDA - Secure DevOps Pipeline

## 0️⃣ PRE-REQUISITOS
```bash
# Verificar Python 3.9+
python --version

# Verificar Git
git --version
```

---

## 1️⃣ SETUP LOCAL (5 minutos)

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Entrenar modelo (⏱️ 5-10 min)
python model/train_model.py

# 5. Ejecutar tests
pytest tests/ -v

# 6. Iniciar app localmente
python run.py app
# Visitar: http://localhost:5000/health
```

---

## 2️⃣ TESTEAR LA API

### Verificar salud
```bash
curl http://localhost:5000/health
```

### Clasificar código (SEGURO)
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"code": "public class Test { }"}'
```

### Clasificar código (VULNERABLE)
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"code": "Runtime.getRuntime().exec(cmd);"}'
```

---

## 3️⃣ SETUP EN GITHUB

### 3.1 Crear repositorio
```bash
git init
git add .
git commit -m "Initial commit: Secure DevOps Pipeline"
git branch -M main
git remote add origin https://github.com/TuUsuario/PRY_P2.git
git push -u origin main
```

### 3.2 Crear ramas
```bash
git checkout -b dev
git push -u origin dev

git checkout -b test
git push -u origin test
```

### 3.3 Branch Protection Rules
En GitHub → Settings → Branches:
- **Rama main:** Requerir PR + reviews
- **Rama test:** Requerir PR + checks de GitHub Actions

---

## 4️⃣ DESPLEGAR EN RENDER

### 4.1 Conectar Render
1. Ir a https://render.com
2. Sign up con GitHub
3. Click "New +" → "Web Service"
4. Seleccionar repositorio
5. Configurar:
   ```
   Name:              secure-devops-pipeline
   Root Directory:    (dejar vacío)
   Environment:       Python 3.9
   Build Command:     pip install -r requirements.txt
   Start Command:     python start.py
   ```
6. Click "Create Web Service"

### 4.2 Verificar despliegue
- Esperar 2-3 minutos
- Ir a: https://secure-devops-pipeline.onrender.com/health
- Debe retornar JSON con `"model_loaded": true`

---

## 5️⃣ FLUJO DE DESARROLLO

### Hacer un cambio
```bash
# 1. Desde dev
git checkout dev

# 2. Crear feature
git checkout -b feature/my-feature

# 3. Cambios
# editar código...

# 4. Push
git add .
git commit -m "Add new feature"
git push origin feature/my-feature

# 5. GitHub: Crear PR de feature→test
```

### Pipeline automático
✅ Security Check (ML model)
↓
✅ Tests (pytest)
↓
✅ Merge a test
↓
✅ Deploy a Render

---

## 6️⃣ ESTRUCTURA DE CARPETAS

```
PRY_P2/
├── app/                          # API Flask
│   ├── app.py                    # Servidor principal
│   └── config.py                 # Configuración
├── model/                        # Modelo ML
│   ├── train_model.py            # Script entrenamiento
│   ├── classifier_model.joblib   # ⬅️ Auto-generado
│   ├── scaler.joblib             # ⬅️ Auto-generado
│   └── feature_names.json        # ⬅️ Auto-generado
├── security_checker/             # Extractor features
│   ├── __init__.py
│   └── feature_extractor.py      # Análisis código
├── notebooks/
│   └── 01_EDA_Vulnerability_Dataset.ipynb  # Análisis
├── tests/                        # Unit tests
│   ├── test_feature_extractor.py
│   └── test_app.py
├── .github/workflows/
│   └── main.yml                  # CI/CD pipeline
├── requirements.txt              # Dependencias
├── Procfile                      # Config Render
├── start.py                      # Script inicio
└── run.py                        # Helpers
```

---

## 7️⃣ COMANDOS ÚTILES

```bash
# Entrenar modelo
python model/train_model.py

# Ejecutar tests
pytest tests/ -v

# Ejecutar app
python run.py app

# Ejecutar tests
python run.py test

# Limpiar cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name *.pyc -delete

# Ver logs de Render
# En Render dashboard → Logs
```

---

## 8️⃣ TROUBLESHOOTING

### Error: "Modelo no encontrado"
```bash
# Solución: Entrenar modelo
python model/train_model.py
```

### Error: "Puerto 5000 en uso"
```bash
# Windows
netstat -ano | findstr :5000

# Mac/Linux
lsof -i :5000
```

### Error en Render: "Timeout"
- Aumentar timeout en Render settings
- O entrenar modelo localmente y pushear a GitHub

### Tests fallan
```bash
# Ejecutar con verbose
pytest tests/ -vv --tb=long
```

---

## 9️⃣ ENDPOINTS API

### GET /health
- Status de la app
- Si modelo está cargado

### POST /predict
```json
{
  "code": "public class Test { }"
}
```
Retorna:
```json
{
  "prediction": "SEGURO",
  "confidence": 0.95,
  "probabilities": {"SEGURO": 0.95, "VULNERABLE": 0.05}
}
```

### POST /batch-predict
```json
{
  "codes": [
    {"name": "test1", "code": "..."},
    {"name": "test2", "code": "..."}
  ]
}
```

### GET /model-info
- Información del modelo
- Nombres de features

---

## 🔟 CHECKLIST FINAL

Antes de entregar:

- [ ] EDA notebook ejecutado (notebooks/01_EDA_*.ipynb)
- [ ] Modelo entrenado con accuracy ≥82%
- [ ] API funcionando en Render
- [ ] Tests pasando
- [ ] GitHub Actions pipeline funcionando
- [ ] Branch protection rules activadas
- [ ] README actualizado
- [ ] Deploy en Render online y accesible

---

## 📞 SOPORTE

**Errores o dudas:**
1. Revisar logs: `Render → Logs`
2. Ejecutar localmente: `python run.py app`
3. Revisar tests: `pytest tests/ -v`

**Documentación:**
- [Render Docs](https://render.com/docs)
- [Flask Docs](https://flask.palletsprojects.com)
- [XGBoost Docs](https://xgboost.readthedocs.io)

---

**Fecha límite:** 18 de junio de 2026 23:59  
**Profesor:** Geovanny Cudco  
**Asignatura:** Desarrollo de Software Seguro
