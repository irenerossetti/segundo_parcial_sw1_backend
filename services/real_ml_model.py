"""
Modelo Real de Deep Learning para Clasificación de Trámites
Este modelo predice si un trámite será APROBADO o RECHAZADO
basándose en características reales
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

# TensorFlow
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow no disponible")
    class DummyKerasModel:
        pass
    class DummyKeras:
        Model = DummyKerasModel
    keras = DummyKeras

# PyTorch
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    logging.warning("PyTorch no disponible")


logger = logging.getLogger(__name__)


class TramiteDataset:
    """
    Genera dataset sintético para entrenar el modelo
    En producción, esto vendría de la base de datos real
    """
    
    @staticmethod
    def generate_synthetic_data(n_samples: int = 1000) -> pd.DataFrame:
        """
        Genera datos sintéticos de trámites para entrenamiento
        
        Features:
        - risk_score: Score de riesgo (0-100)
        - documents_count: Cantidad de documentos (0-20)
        - completion_time_days: Tiempo de completación estimado (1-30)
        - client_history_score: Historial del cliente (0-100)
        - policy_complexity: Complejidad de la política (1-10)
        - department_load: Carga del departamento (0-100)
        - priority_level: Nivel de prioridad (1-3: BAJA, MEDIA, ALTA)
        
        Target:
        - outcome: APROBADO (1) o RECHAZADO (0)
        """
        np.random.seed(42)
        
        data = {
            'risk_score': np.random.randint(0, 100, n_samples),
            'documents_count': np.random.randint(1, 21, n_samples),
            'completion_time_days': np.random.randint(1, 31, n_samples),
            'client_history_score': np.random.randint(0, 100, n_samples),
            'policy_complexity': np.random.randint(1, 11, n_samples),
            'department_load': np.random.randint(0, 100, n_samples),
            'priority_level': np.random.randint(1, 4, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generar target basado en lógica de negocio
        # Trámites con bajo riesgo, buenos docs, buen historial → APROBADO
        df['outcome'] = 0  # Default: RECHAZADO
        
        # Reglas de aprobación:
        df.loc[
            (df['risk_score'] < 50) & 
            (df['documents_count'] >= 5) & 
            (df['client_history_score'] > 60),
            'outcome'
        ] = 1
        
        # Agregar algo de ruido (10% aleatorio)
        noise_indices = np.random.choice(df.index, size=int(n_samples * 0.1), replace=False)
        df.loc[noise_indices, 'outcome'] = 1 - df.loc[noise_indices, 'outcome']
        
        return df


class TramiteClassifierTensorFlow:
    """
    Clasificador de trámites usando TensorFlow/Keras
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'risk_score', 'documents_count', 'completion_time_days',
            'client_history_score', 'policy_complexity', 
            'department_load', 'priority_level'
        ]
        self.is_trained = False
        
    def build_model(self, input_dim: int) -> keras.Model:
        """Construye arquitectura del modelo"""
        model = keras.Sequential([
            layers.Input(shape=(input_dim,)),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='sigmoid')  # Binary classification
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray, y_val: np.ndarray,
              epochs: int = 50, batch_size: int = 32) -> Dict[str, Any]:
        """
        Entrena el modelo
        """
        logger.info("🧠 Entrenando modelo TensorFlow...")
        
        # Normalizar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Construir modelo
        self.model = self.build_model(X_train.shape[1])
        
        # Callbacks
        early_stop = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Entrenar
        history = self.model.fit(
            X_train_scaled, y_train,
            validation_data=(X_val_scaled, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Evaluar
        val_loss, val_accuracy, val_auc = self.model.evaluate(
            X_val_scaled, y_val, verbose=0
        )
        
        self.is_trained = True
        
        logger.info(f"✓ Entrenamiento completado - Accuracy: {val_accuracy:.4f}, AUC: {val_auc:.4f}")
        
        return {
            'framework': 'TensorFlow',
            'accuracy': float(val_accuracy),
            'auc': float(val_auc),
            'loss': float(val_loss),
            'epochs_trained': len(history.history['loss']),
            'training_time': datetime.now().isoformat()
        }
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Realiza predicciones
        Returns: (predictions, probabilities)
        """
        if not self.is_trained:
            raise ValueError("Modelo no entrenado")
        
        X_scaled = self.scaler.transform(X)
        probabilities = self.model.predict(X_scaled, verbose=0)
        predictions = (probabilities > 0.5).astype(int).flatten()
        
        return predictions, probabilities.flatten()
    
    def save_model(self, path: str):
        """Guarda el modelo entrenado"""
        if not self.is_trained:
            raise ValueError("Modelo no entrenado")
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        # Guardar modelo Keras
        self.model.save(f"{path}_model.h5")
        
        # Guardar scaler
        with open(f"{path}_scaler.pkl", 'wb') as f:
            pickle.dump(self.scaler, f)
        
        logger.info(f"✓ Modelo guardado en {path}")
    
    def load_model(self, path: str):
        """Carga un modelo previamente entrenado"""
        self.model = keras.models.load_model(f"{path}_model.h5")
        
        with open(f"{path}_scaler.pkl", 'rb') as f:
            self.scaler = pickle.load(f)
        
        self.is_trained = True
        logger.info(f"✓ Modelo cargado desde {path}")


class TramiteClassifierPyTorch(nn.Module):
    """
    Clasificador de trámites usando PyTorch
    """
    
    def __init__(self, input_dim: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.network(x)


class ModelTrainer:
    """
    Clase principal para entrenar y gestionar modelos
    """
    
    def __init__(self, model_type: str = 'tensorflow'):
        """
        Args:
            model_type: 'tensorflow' o 'pytorch'
        """
        self.model_type = model_type
        self.model = None
        self.metrics = {}
        
        if model_type == 'tensorflow' and not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow no está disponible")
        elif model_type == 'pytorch' and not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch no está disponible")
    
    def prepare_data(self, n_samples: int = 1000) -> Tuple:
        """
        Prepara datos para entrenamiento
        """
        logger.info(f"📊 Generando {n_samples} muestras de datos...")
        
        # Generar datos
        df = TramiteDataset.generate_synthetic_data(n_samples)
        
        # Separar features y target
        X = df[['risk_score', 'documents_count', 'completion_time_days',
                'client_history_score', 'policy_complexity', 
                'department_load', 'priority_level']].values
        y = df['outcome'].values
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"✓ Train: {len(X_train)} | Test: {len(X_test)}")
        logger.info(f"✓ Distribución clases - Aprobados: {y.sum()}/{len(y)} ({y.sum()/len(y)*100:.1f}%)")
        
        return X_train, X_test, y_train, y_test
    
    def train_model(self, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        """
        Entrena el modelo según el tipo especificado
        """
        if self.model_type == 'tensorflow':
            self.model = TramiteClassifierTensorFlow()
            metrics = self.model.train(X_train, y_train, X_test, y_test)
        else:
            raise NotImplementedError("PyTorch trainer aún no implementado")
        
        # Calcular métricas adicionales
        predictions, probabilities = self.model.predict(X_test)
        
        report = classification_report(y_test, predictions, output_dict=True)
        conf_matrix = confusion_matrix(y_test, predictions)
        
        metrics.update({
            'precision': report['1']['precision'],
            'recall': report['1']['recall'],
            'f1_score': report['1']['f1-score'],
            'confusion_matrix': conf_matrix.tolist()
        })
        
        self.metrics = metrics
        return metrics
    
    def save_model(self, path: str = 'models/tramite_classifier'):
        """Guarda el modelo entrenado"""
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        self.model.save_model(path)
        
        # Guardar métricas
        with open(f"{path}_metrics.pkl", 'wb') as f:
            pickle.dump(self.metrics, f)
    
    def load_model(self, path: str = 'models/tramite_classifier'):
        """Carga un modelo previamente entrenado"""
        if self.model_type == 'tensorflow':
            self.model = TramiteClassifierTensorFlow()
            self.model.load_model(path)
        
        # Cargar métricas
        try:
            with open(f"{path}_metrics.pkl", 'rb') as f:
                self.metrics = pickle.load(f)
        except FileNotFoundError:
            logger.warning("Métricas no encontradas")


# ============= FUNCIÓN PRINCIPAL DE ENTRENAMIENTO =============

def train_tramite_classifier(n_samples: int = 2000, model_type: str = 'tensorflow') -> Dict[str, Any]:
    """
    Función principal para entrenar el modelo de clasificación de trámites
    
    Args:
        n_samples: Número de muestras de entrenamiento
        model_type: 'tensorflow' o 'pytorch'
    
    Returns:
        Métricas del modelo entrenado
    """
    logger.info("=" * 60)
    logger.info("🚀 ENTRENAMIENTO DE MODELO DE CLASIFICACIÓN DE TRÁMITES")
    logger.info("=" * 60)
    
    trainer = ModelTrainer(model_type=model_type)
    
    # Preparar datos
    X_train, X_test, y_train, y_test = trainer.prepare_data(n_samples)
    
    # Entrenar
    metrics = trainer.train_model(X_train, X_test, y_train, y_test)
    
    # Guardar
    trainer.save_model()
    
    logger.info("=" * 60)
    logger.info("✅ ENTRENAMIENTO COMPLETADO")
    logger.info(f"📊 Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"📊 Precision: {metrics['precision']:.4f}")
    logger.info(f"📊 Recall: {metrics['recall']:.4f}")
    logger.info(f"📊 F1-Score: {metrics['f1_score']:.4f}")
    logger.info("=" * 60)
    
    return metrics


# Instancia global del modelo entrenado
_trained_model = None

def get_trained_model() -> TramiteClassifierTensorFlow:
    """Obtiene instancia del modelo entrenado (singleton)"""
    global _trained_model
    
    if _trained_model is None:
        _trained_model = TramiteClassifierTensorFlow()
        try:
            _trained_model.load_model('models/tramite_classifier')
            logger.info("✓ Modelo cargado exitosamente")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo cargar modelo: {e}")
            logger.info("🔧 Entrenando nuevo modelo...")
            train_tramite_classifier()
            _trained_model.load_model('models/tramite_classifier')
    
    return _trained_model
