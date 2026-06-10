"""
Script para entrenar el modelo LSTM de predicción de cuellos de botella
Ejecutar: python train_lstm.py
"""

import logging
from services.bottleneck_lstm import bottleneck_predictor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧠 ENTRENAMIENTO DE MODELO LSTM - CUELLOS DE BOTELLA")
    print("="*60 + "\n")
    
    try:
        # Generar datos sintéticos
        print("📊 Generando datos de series temporales...")
        df = bottleneck_predictor.generate_synthetic_time_series(
            n_days=90,
            n_nodes=5
        )
        
        print(f"✓ Generados {len(df)} registros")
        print(f"✓ Nodos: {bottleneck_predictor.node_names}\n")
        
        # Entrenar modelo
        print("🚀 Entrenando modelo LSTM...")
        metrics = bottleneck_predictor.train(df, epochs=50, batch_size=32)
        
        print("\n" + "="*60)
        print("📊 RESULTADOS DEL ENTRENAMIENTO:")
        print("="*60)
        print(f"✓ Framework: {metrics['framework']}")
        print(f"✓ Loss (MSE): {metrics['loss']:.4f}")
        print(f"✓ MAE: {metrics['mae']:.4f}")
        print(f"✓ Épocas: {metrics['epochs']}")
        print(f"✓ Longitud de secuencia: {metrics['sequence_length']} días")
        print(f"✓ Nodos entrenados: {metrics['nodes_trained']}")
        print("="*60 + "\n")
        
        # Hacer una predicción de prueba
        print("🔮 Predicción de prueba:")
        test_history = [12, 15, 18, 14, 20, 22, 19]
        predictions = bottleneck_predictor.predict_next_days(
            historical_data=test_history,
            n_days_ahead=7
        )
        
        print(f"   Histórico (últimos 7 días): {test_history}")
        print(f"   Predicción (próximos 7 días): {[f'{p:.1f}' for p in predictions]}")
        
        # Analizar riesgo
        risk = bottleneck_predictor.detect_bottleneck_risk(predictions)
        print(f"\n   Nivel de riesgo: {risk['risk_level']}")
        print(f"   Días con riesgo: {risk['total_risk_days']}")
        
        if risk['recommendations']:
            print(f"\n   Recomendaciones:")
            for rec in risk['recommendations'][:2]:
                print(f"   • {rec}")
        
        print("\n" + "="*60)
        print("✅ MODELO LSTM ENTRENADO EXITOSAMENTE")
        print("="*60)
        print("\n💡 El modelo está listo para predecir cuellos de botella")
        print("   Usa la API: POST /api/bottleneck/predict")
        print("\n")
        
    except Exception as e:
        print("\n❌ ERROR durante el entrenamiento:")
        print(f"   {str(e)}")
        print("\nVerifica que TensorFlow esté instalado:")
        print("   pip install tensorflow\n")
        exit(1)
