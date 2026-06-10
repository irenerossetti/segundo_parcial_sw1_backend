"""
Predictor de Cuellos de Botella usando LSTM
Predice acumulación de trámites en nodos del workflow
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow no disponible para LSTM")
    class DummySequential:
        pass
    Sequential = DummySequential


class BottleneckLSTMPredictor:
    """
    Predictor de cuellos de botella usando LSTM (Long Short-Term Memory)
    Analiza series temporales de trámites en nodos del workflow
    """
    
    def __init__(self, sequence_length: int = 7):
        """
        Args:
            sequence_length: Número de días históricos para predecir (ventana temporal)
        """
        self.sequence_length = sequence_length
        self.model = None
        self.is_trained = False
        self.node_names = []
        
    def build_model(self, n_features: int) -> Sequential:
        """
        Construye arquitectura LSTM
        
        Args:
            n_features: Número de features de entrada
        
        Returns:
            Modelo LSTM compilado
        """
        model = Sequential([
            # Primera capa LSTM
            LSTM(50, activation='relu', return_sequences=True, 
                 input_shape=(self.sequence_length, n_features)),
            Dropout(0.2),
            
            # Segunda capa LSTM
            LSTM(50, activation='relu'),
            Dropout(0.2),
            
            # Capas densas
            Dense(25, activation='relu'),
            Dense(1)  # Predicción: número de trámites acumulados
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def generate_synthetic_time_series(self, 
                                       n_days: int = 90,
                                       n_nodes: int = 5) -> pd.DataFrame:
        """
        Genera datos sintéticos de series temporales para entrenamiento
        
        Args:
            n_days: Número de días de datos
            n_nodes: Número de nodos del workflow
        
        Returns:
            DataFrame con histórico de trámites por nodo
        """
        np.random.seed(42)
        
        dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')
        
        data = []
        self.node_names = [f'Nodo_{i+1}' for i in range(n_nodes)]
        
        for i, node in enumerate(self.node_names):
            # Simular patrones realistas
            base = 10 + i * 5
            trend = np.linspace(0, 5, n_days)
            seasonal = 3 * np.sin(np.linspace(0, 4*np.pi, n_days))
            noise = np.random.normal(0, 2, n_days)
            
            # Simular cuellos de botella ocasionales
            bottlenecks = np.zeros(n_days)
            bottleneck_days = np.random.choice(n_days, size=int(n_days * 0.1), replace=False)
            bottlenecks[bottleneck_days] = np.random.uniform(10, 20, len(bottleneck_days))
            
            # Combinar componentes
            tramites = base + trend + seasonal + noise + bottlenecks
            tramites = np.maximum(tramites, 0)  # No negativos
            
            for date, count in zip(dates, tramites):
                data.append({
                    'date': date,
                    'node': node,
                    'tramites_count': int(count),
                    'day_of_week': date.dayofweek,
                    'is_bottleneck': 1 if count > base + 10 else 0
                })
        
        df = pd.DataFrame(data)
        logger.info(f"✓ Generados {len(df)} registros de {n_days} días para {n_nodes} nodos")
        
        return df
    
    def prepare_sequences(self, 
                         data: np.ndarray,
                         sequence_length: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara secuencias para LSTM
        
        Args:
            data: Array 1D con valores temporales
            sequence_length: Longitud de la secuencia (ventana)
        
        Returns:
            (X, y) donde X son las secuencias y y los valores a predecir
        """
        if sequence_length is None:
            sequence_length = self.sequence_length
        
        X, y = [], []
        
        for i in range(len(data) - sequence_length):
            X.append(data[i:i + sequence_length])
            y.append(data[i + sequence_length])
        
        return np.array(X), np.array(y)
    
    def train(self, 
             df: pd.DataFrame,
             epochs: int = 50,
             batch_size: int = 32) -> Dict[str, Any]:
        """
        Entrena el modelo LSTM
        
        Args:
            df: DataFrame con histórico de trámites
            epochs: Número de épocas de entrenamiento
            batch_size: Tamaño del lote
        
        Returns:
            Métricas de entrenamiento
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow no disponible")
        
        logger.info("🧠 Entrenando modelo LSTM para predicción de cuellos de botella...")
        
        # Preparar datos por nodo
        all_X, all_y = [], []
        
        for node in self.node_names:
            node_data = df[df['node'] == node].sort_values('date')
            tramites = node_data['tramites_count'].values
            
            # Normalizar (0-1)
            tramites_norm = (tramites - tramites.min()) / (tramites.max() - tramites.min() + 1e-8)
            
            # Crear secuencias
            X, y = self.prepare_sequences(tramites_norm)
            
            all_X.append(X)
            all_y.append(y)
        
        # Combinar todos los nodos
        X_train = np.vstack(all_X)
        y_train = np.concatenate(all_y)
        
        # Reshape para LSTM: (samples, sequence_length, features)
        X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        
        logger.info(f"✓ Datos preparados: X_train shape={X_train.shape}, y_train shape={y_train.shape}")
        
        # Construir modelo
        self.model = self.build_model(n_features=1)
        
        # Entrenar
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=0
        )
        
        self.is_trained = True
        
        final_loss = history.history['loss'][-1]
        final_mae = history.history['mae'][-1]
        
        logger.info(f"✓ Modelo LSTM entrenado - Loss: {final_loss:.4f}, MAE: {final_mae:.4f}")
        
        return {
            'framework': 'TensorFlow LSTM',
            'loss': float(final_loss),
            'mae': float(final_mae),
            'epochs': epochs,
            'sequence_length': self.sequence_length,
            'nodes_trained': len(self.node_names)
        }
    
    def predict_next_days(self, 
                         historical_data: List[float],
                         n_days_ahead: int = 7) -> List[float]:
        """
        Predice los próximos N días
        
        Args:
            historical_data: Últimos `sequence_length` días de datos
            n_days_ahead: Días a predecir hacia adelante
        
        Returns:
            Lista con predicciones
        """
        if not self.is_trained:
            raise ValueError("Modelo no entrenado")
        
        if len(historical_data) < self.sequence_length:
            raise ValueError(f"Se requieren al menos {self.sequence_length} días de datos históricos")
        
        # Normalizar datos históricos
        hist_array = np.array(historical_data[-self.sequence_length:])
        hist_min, hist_max = hist_array.min(), hist_array.max()
        hist_norm = (hist_array - hist_min) / (hist_max - hist_min + 1e-8)
        
        predictions = []
        current_sequence = hist_norm.copy()
        
        # Predecir iterativamente
        for _ in range(n_days_ahead):
            # Reshape para LSTM
            X = current_sequence.reshape(1, self.sequence_length, 1)
            
            # Predecir siguiente valor
            pred_norm = self.model.predict(X, verbose=0)[0][0]
            
            # Desnormalizar
            pred = pred_norm * (hist_max - hist_min) + hist_min
            predictions.append(float(max(0, pred)))
            
            # Actualizar secuencia (sliding window)
            current_sequence = np.roll(current_sequence, -1)
            current_sequence[-1] = pred_norm
        
        return predictions
    
    def detect_bottleneck_risk(self, 
                              predictions: List[float],
                              threshold_multiplier: float = 1.5) -> Dict[str, Any]:
        """
        Detecta riesgo de cuello de botella en las predicciones
        
        Args:
            predictions: Predicciones futuras
            threshold_multiplier: Multiplicador sobre promedio para detectar anomalía
        
        Returns:
            Análisis de riesgo
        """
        avg_pred = np.mean(predictions)
        max_pred = max(predictions)
        threshold = avg_pred * threshold_multiplier
        
        # Detectar días con riesgo
        risk_days = []
        for i, pred in enumerate(predictions):
            if pred > threshold:
                risk_days.append({
                    'day': i + 1,
                    'predicted_count': pred,
                    'excess_percentage': ((pred - avg_pred) / avg_pred) * 100
                })
        
        # Determinar nivel de riesgo
        if max_pred > avg_pred * 2:
            risk_level = 'CRITICAL'
        elif max_pred > avg_pred * 1.5:
            risk_level = 'HIGH'
        elif max_pred > avg_pred * 1.2:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_level': risk_level,
            'average_predicted': avg_pred,
            'max_predicted': max_pred,
            'threshold': threshold,
            'risk_days': risk_days,
            'total_risk_days': len(risk_days),
            'recommendations': self._generate_recommendations(risk_level, risk_days)
        }
    
    def _generate_recommendations(self, risk_level: str, risk_days: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en el riesgo"""
        recommendations = []
        
        if risk_level == 'CRITICAL':
            recommendations.append("⚠️ URGENTE: Asignar recursos adicionales inmediatamente")
            recommendations.append("Considerar procesamiento en paralelo o turnos extra")
        elif risk_level == 'HIGH':
            recommendations.append("Incrementar personal en los próximos días")
            recommendations.append("Priorizar trámites urgentes")
        elif risk_level == 'MEDIUM':
            recommendations.append("Monitorear de cerca la acumulación")
            recommendations.append("Preparar recursos de contingencia")
        else:
            recommendations.append("Flujo normal - mantener monitoreo rutinario")
        
        if len(risk_days) > 3:
            recommendations.append(f"Se detectan {len(risk_days)} días con alto riesgo")
        
        return recommendations


# Instancia global
bottleneck_predictor = BottleneckLSTMPredictor()
