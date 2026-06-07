"""
API Flask para Classificación de Vulnerabilidades
Despliegue en Render
"""
import os
import json
import joblib
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import sys

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security_checker.feature_extractor import JavaCodeAnalyzer

# Crear app Flask
app = Flask(__name__)
CORS(app)

# Variables globales
MODEL = None
FEATURE_NAMES = None
MODEL_LOADED = False

def load_model():
    """Carga el modelo entrenado"""
    global MODEL, FEATURE_NAMES, MODEL_LOADED
    
    model_path = Path(__file__).parent.parent / 'model' / 'classifier_model.joblib'
    features_path = Path(__file__).parent.parent / 'model' / 'feature_names.json'
    
    try:
        if model_path.exists() and features_path.exists():
            MODEL = joblib.load(model_path)
            with open(features_path, 'r') as f:
                FEATURE_NAMES = json.load(f)
            MODEL_LOADED = True
            print(f"✓ Modelo cargado desde: {model_path}")
            print(f"✓ Features cargadas: {len(FEATURE_NAMES)} características")
            return True
        else:
            print(f"✗ Archivo modelo no encontrado en: {model_path}")
            return False
    except Exception as e:
        print(f"✗ Error cargando modelo: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': MODEL_LOADED,
        'timestamp': pd.Timestamp.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint para clasificar código
    Espera: {"code": "código Java aquí"}
    """
    if not MODEL_LOADED:
        return jsonify({
            'error': 'Modelo no cargado',
            'status': 'error'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                'error': 'Campo "code" requerido',
                'status': 'error'
            }), 400
        
        code = data['code']
        
        if not code or len(code.strip()) == 0:
            return jsonify({
                'error': 'Código vacío',
                'status': 'error'
            }), 400
        
        # Extraer características
        features_dict = JavaCodeAnalyzer.extract_features(code)
        features_array = np.array([features_dict[name] for name in FEATURE_NAMES]).reshape(1, -1)
        
        # Predicción
        prediction = MODEL.predict(features_array)[0]
        probability = MODEL.predict_proba(features_array)[0]
        
        # Mapear predicción
        class_names = ['SEGURO', 'VULNERABLE']
        predicted_class = class_names[prediction]
        confidence = float(max(probability))
        
        return jsonify({
            'status': 'success',
            'prediction': predicted_class,
            'confidence': confidence,
            'probabilities': {
                'SEGURO': float(probability[0]),
                'VULNERABLE': float(probability[1])
            },
            'features_extracted': len(features_dict),
            'code_length': len(code),
            'code_lines': code.count('\n') + 1
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """
    Endpoint para clasificar múltiples códigos
    Espera: {"codes": [{"name": "...", "code": "..."}, ...]}
    """
    if not MODEL_LOADED:
        return jsonify({
            'error': 'Modelo no cargado',
            'status': 'error'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'codes' not in data or not isinstance(data['codes'], list):
            return jsonify({
                'error': 'Campo "codes" requerido (lista)',
                'status': 'error'
            }), 400
        
        results = []
        
        for item in data['codes']:
            if 'code' not in item:
                continue
            
            code = item['code']
            name = item.get('name', f'code_{len(results)}')
            
            # Extraer características
            features_dict = JavaCodeAnalyzer.extract_features(code)
            features_array = np.array([features_dict[name_feat] for name_feat in FEATURE_NAMES]).reshape(1, -1)
            
            # Predicción
            prediction = MODEL.predict(features_array)[0]
            probability = MODEL.predict_proba(features_array)[0]
            
            class_names = ['SEGURO', 'VULNERABLE']
            predicted_class = class_names[prediction]
            confidence = float(max(probability))
            
            results.append({
                'name': name,
                'prediction': predicted_class,
                'confidence': confidence,
                'probabilities': {
                    'SEGURO': float(probability[0]),
                    'VULNERABLE': float(probability[1])
                }
            })
        
        return jsonify({
            'status': 'success',
            'total': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/model-info', methods=['GET'])
def model_info():
    """Retorna información del modelo"""
    if not MODEL_LOADED:
        return jsonify({
            'error': 'Modelo no cargado',
            'status': 'error'
        }), 500
    
    return jsonify({
        'status': 'success',
        'model_type': type(MODEL).__name__,
        'features_count': len(FEATURE_NAMES),
        'feature_names': FEATURE_NAMES,
        'classes': ['SEGURO', 'VULNERABLE']
    })

@app.errorhandler(404)
def not_found(error):
    """Manejo de 404"""
    return jsonify({
        'error': 'Endpoint no encontrado',
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de 500"""
    return jsonify({
        'error': 'Error interno del servidor',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    import pandas as pd
    
    # Cargar modelo
    if not load_model():
        print("⚠️  Advertencia: Modelo no cargado. Solo /health disponible")
    
    # Configurar puerto
    port = int(os.getenv('PORT', 5000))
    
    # Ejecutar app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') == 'development'
    )

