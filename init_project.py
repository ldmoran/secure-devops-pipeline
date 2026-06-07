"""
Script para inicializar el proyecto
Entrena el modelo automáticamente si no existe
"""
import os
import sys
from pathlib import Path

def init_project():
    """Inicializa el proyecto"""
    print("🔧 Inicializando proyecto...")
    
    # Crear directorios necesarios
    dirs_to_create = [
        'data/raw',
        'data/processed',
        'model',
        'logs'
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Directorio: {dir_path}")
    
    # Verificar si existe el dataset
    dataset_path = Path('data/raw/vulnerability_fix_dataset.csv')
    if not dataset_path.exists():
        print("\n⚠️  Dataset no encontrado en data/raw/")
        print("   Descárgalo desde: https://www.kaggle.com/datasets/...")
        return False
    
    # Verificar si existe el modelo
    model_path = Path('model/classifier_model.joblib')
    if not model_path.exists():
        print("\n📚 Entrenando modelo...")
        try:
            os.chdir('model')
            os.system(f'{sys.executable} train_model.py')
            os.chdir('..')
            print("✓ Modelo entrenado exitosamente")
        except Exception as e:
            print(f"❌ Error entrenando modelo: {e}")
            return False
    else:
        print("✓ Modelo existente encontrado")
    
    print("\n✅ Inicialización completada")
    return True

if __name__ == '__main__':
    init_project()
