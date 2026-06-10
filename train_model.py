"""
Script para entrenar el modelo de Deep Learning
Ejecutar: python train_model.py
"""

import logging
from services.real_ml_model import train_tramite_classifier

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 INICIANDO ENTRENAMIENTO DE MODELO")
    print("="*60 + "\n")
    
    # Entrenar con 2000 muestras
    metrics = train_tramite_classifier(n_samples=2000, model_type='tensorflow')
    
    print("\n" + "="*60)
    print("📊 RESULTADOS FINALES:")
    print("="*60)
    print(f"✓ Framework: {metrics['framework']}")
    print(f"✓ Accuracy: {metrics['accuracy']:.2%}")
    print(f"✓ AUC: {metrics['auc']:.4f}")
    print(f"✓ Precision: {metrics['precision']:.2%}")
    print(f"✓ Recall: {metrics['recall']:.2%}")
    print(f"✓ F1-Score: {metrics['f1_score']:.4f}")
    print(f"✓ Épocas entrenadas: {metrics['epochs_trained']}")
    print("="*60 + "\n")
    
    print("✅ Modelo guardado en: models/tramite_classifier")
    print("📁 Archivos generados:")
    print("   - tramite_classifier_model.h5")
    print("   - tramite_classifier_scaler.pkl")
    print("   - tramite_classifier_metrics.pkl")
    print("\n🎉 ¡Listo para usar en producción!\n")
