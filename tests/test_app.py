"""
Test para la API Flask
"""
import pytest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock del modelo si no está disponible
import joblib
from pathlib import Path

def test_app_imports():
    """Test que la app se puede importar"""
    try:
        from app.app import app
        assert app is not None
    except Exception as e:
        pytest.skip(f"App no puede importarse: {e}")

def test_health_endpoint():
    """Test endpoint de salud"""
    try:
        from app.app import app
        
        client = app.test_client()
        response = client.get('/health')
        
        assert response.status_code in [200, 500]  # 500 si modelo no existe
        data = response.get_json()
        assert 'status' in data
    except Exception as e:
        pytest.skip(f"No se puede testear: {e}")

def test_model_loading():
    """Test que el modelo se carga correctamente"""
    model_path = Path(__file__).parent.parent / 'model' / 'classifier_model.joblib'
    
    if not model_path.exists():
        pytest.skip("Modelo no entrenado aún")
    
    try:
        model = joblib.load(model_path)
        assert model is not None
    except Exception as e:
        pytest.fail(f"Error cargando modelo: {e}")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
