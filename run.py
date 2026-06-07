"""
Wrapper para ejecutar tests rápidamente
"""
import subprocess
import sys

def run_tests():
    """Ejecuta tests"""
    print("🧪 Ejecutando tests...\n")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
        cwd='.'
    )
    return result.returncode

def run_model_training():
    """Entrena el modelo"""
    print("🤖 Entrenando modelo...\n")
    result = subprocess.run(
        [sys.executable, 'model/train_model.py'],
        cwd='.'
    )
    return result.returncode

def run_app():
    """Ejecuta la app"""
    print("🌐 Iniciando app...\n")
    result = subprocess.run(
        [sys.executable, '-m', 'flask', '--app', 'app.app', 'run', '--debug'],
        cwd='app'
    )
    return result.returncode

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python run.py <comando>")
        print("Comandos:")
        print("  - test: Ejecutar tests")
        print("  - train: Entrenar modelo")
        print("  - app: Ejecutar aplicación")
        sys.exit(1)
    
    comando = sys.argv[1]
    
    if comando == 'test':
        sys.exit(run_tests())
    elif comando == 'train':
        sys.exit(run_model_training())
    elif comando == 'app':
        sys.exit(run_app())
    else:
        print(f"Comando desconocido: {comando}")
        sys.exit(1)
