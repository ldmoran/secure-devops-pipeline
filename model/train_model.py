"""
Script para entrenar el modelo de clasificación
Ejecutar desde el directorio raíz del proyecto
"""
import os
import sys
import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from security_checker.feature_extractor import JavaCodeAnalyzer

def load_dataset(csv_path: str) -> pd.DataFrame:
    """Carga el dataset CSV"""
    print(f"📂 Cargando dataset desde: {csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8', on_bad_lines='skip')
    print(f"✓ Dataset cargado: {df.shape[0]} registros, {df.shape[1]} columnas")
    return df

def prepare_data(df: pd.DataFrame) -> tuple:
    """
    Prepara datos para entrenamiento
    Extrae features del código
    """
    print("\n🔍 Extrayendo características...")
    
    # Identificar columnas de código y etiqueta
    code_col = "code"
    label_col = "label"
        
    print(f"  • Usando columna de código: {code_col}")
    print(f"  • Usando columna de etiqueta: {label_col}")
        
        # Limpiar datos
    df = df.dropna(subset=[code_col, label_col])
    print(f"  • Después de limpiar: {df.shape[0]} registros")
    
    # Extraer características
    features_list = []
    valid_indices = []
    
    for idx, (i, row) in enumerate(df.iterrows()):
        try:
            code = str(row[code_col])
            if len(code.strip()) > 0:
                features = JavaCodeAnalyzer.extract_features(code)
                features_list.append(features)
                valid_indices.append(i)
                
                if (idx + 1) % max(1, len(df) // 10) == 0:
                    print(f"    Procesados: {idx + 1}/{len(df)} ({100*(idx+1)/len(df):.1f}%)")
        except:
            continue
    
    # Crear DataFrame con features
    X = pd.DataFrame(features_list)
    feature_names = sorted(X.columns.tolist())
    X = X[feature_names]
    
    # Crear etiquetas (mapear a binario: VULNERABLE=1, SEGURO=0)
    y = df.loc[valid_indices, label_col]
    
    # Mapear etiquetas a binario
    y = y.astype(int)
    
    print(f"\n✓ Características extraídas: {len(feature_names)}")
    print(f"  • Distribución de clases:")
    print(f"    - SEGURO (0): {(y == 0).sum()}")
    print(f"    - VULNERABLE (1): {(y == 1).sum()}")
    
    return X, y, feature_names

def train_model(X: pd.DataFrame, y: pd.Series, feature_names: list) -> tuple:
    """Entrena el modelo"""
    print("\n🤖 Dividiendo datos...")
    
    # Split train-test (80-20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"  • Entrenamiento: {X_train.shape[0]} registros")
    print(f"  • Prueba: {X_test.shape[0]} registros")
    
    # Normalizar
    print("\n📊 Normalizando características...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Entrenar modelo XGBoost (mejor para clasificación binaria)
    print("\n⚙️  Entrenando modelo XGBoost...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss',
        n_jobs=-1
    )
    
    model.fit(
        X_train_scaled, y_train,
        eval_set=[(X_test_scaled, y_test)],
        verbose=50
    )
    
    # Evaluación
    print("\n📈 Evaluando modelo...")
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"\n  • Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  • Precision: {precision:.4f}")
    print(f"  • Recall: {recall:.4f}")
    print(f"  • F1-Score: {f1:.4f}")
    
    # Cross-validation
    print("\n🔄 Cross-validation (5-fold)...")
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')
    print(f"  • CV Scores: {cv_scores}")
    print(f"  • Media CV: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Matriz de confusión
    print("\n🎯 Matriz de Confusión:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Reporte
    print("\n📋 Reporte de Clasificación:")
    print(classification_report(y_test, y_pred, target_names=['SEGURO', 'VULNERABLE']))
    
    return model, scaler, accuracy

def save_model(model, scaler, feature_names, output_dir: str = 'model'):
    """Guarda el modelo"""
    print(f"\n💾 Guardando modelo...")
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Guardar modelo
    model_file = output_path / 'classifier_model.joblib'
    joblib.dump(model, model_file)
    print(f"  ✓ Modelo: {model_file}")
    
    # Guardar scaler
    scaler_file = output_path / 'scaler.joblib'
    joblib.dump(scaler, scaler_file)
    print(f"  ✓ Scaler: {scaler_file}")
    
    # Guardar feature names
    features_file = output_path / 'feature_names.json'
    with open(features_file, 'w') as f:
        json.dump(feature_names, f, indent=2)
    print(f"  ✓ Feature names: {features_file}")
    
    print("\n✅ Modelo entrenado y guardado exitosamente")

def main():
    """Función principal"""
    print("="*70)
    print("ENTRENAMIENTO DE MODELO DE CLASIFICACIÓN DE VULNERABILIDADES")
    print("="*70)
    
    # Ruta del dataset
    dataset_path = Path(__file__).parent.parent / 'data' / 'processed' / 'security_dataset.csv'
    
    if not dataset_path.exists():
        print(f"❌ Dataset no encontrado en: {dataset_path}")
        return
    
    # Cargar dataset
    df = load_dataset(str(dataset_path))
    print(df.columns.tolist())
    print(df.head())
    # Preparar datos
    X, y, feature_names = prepare_data(df)
    
    # Entrenar modelo
    model, scaler, accuracy = train_model(X, y, feature_names)
    
    # Guardar modelo
    output_dir = Path(__file__).parent
    save_model(model, scaler, feature_names, str(output_dir))
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE ENTRENAMIENTO")
    print("="*70)
    print(f"✓ Accuracy alcanzada: {accuracy*100:.2f}%")
    print(f"✓ Características: {len(feature_names)}")
    print(f"✓ Modelo tipo: {type(model).__name__}")
    print("="*70)

if __name__ == '__main__':
    main()


