#!/usr/bin/env python
"""
Script de entrada para Render
Ejecuta inicializaciones necesarias antes de iniciar la app
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Script principal"""
    print("🚀 Starting Secure DevOps Pipeline...")
    
    # Crear directorios
    Path('model').mkdir(exist_ok=True)
    Path('data/raw').mkdir(parents=True, exist_ok=True)
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    # Verificar modelo
    model_path = Path('model/classifier_model.joblib')
    if not model_path.exists():
        print("📚 Training model...")
        try:
            result = subprocess.run(
                [sys.executable, 'model/train_model.py'],
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode != 0:
                print("⚠️  Model training had issues but continuing...")
                print(result.stderr[:500])
            else:
                print("✓ Model trained successfully")
        except subprocess.TimeoutExpired:
            print("⚠️  Model training timeout - using default model")
        except Exception as e:
            print(f"⚠️  Could not train model: {e}")
    else:
        print("✓ Model found")
    
    # Iniciar app
    print("\n🌐 Starting Flask app...")
    os.execv(sys.executable, [sys.executable, '-m', 'gunicorn', '--chdir', 'app', 'app:app'])

if __name__ == '__main__':
    main()
