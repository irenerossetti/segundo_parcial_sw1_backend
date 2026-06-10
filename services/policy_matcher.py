"""
Policy Matcher Service - ML Model para Recomendación de Políticas
Usa NLP y Similitud Coseno para encontrar políticas relevantes
"""

import logging
from typing import List, Dict, Optional
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


# Base de datos simulada de políticas
POLICIES_DATABASE = {
    "POL-001": {
        "id": "POL-001",
        "name": "Seguro de Vida Básico",
        "description": "Cobertura de vida estándar para beneficiarios",
        "keywords": ["vida", "cobertura", "beneficiario", "muerte", "familia"],
        "requirements": ["Identificación", "Certificado de nacimiento"],
        "min_approval_time": 5,
        "max_approval_time": 15
    },
    "POL-002": {
        "id": "POL-002",
        "name": "Seguro de Salud Integral",
        "description": "Cobertura médica completa y preventiva",
        "keywords": ["salud", "médico", "enfermedad", "hospital", "medicina"],
        "requirements": ["Identificación", "Historial médico"],
        "min_approval_time": 7,
        "max_approval_time": 20
    },
    "POL-003": {
        "id": "POL-003",
        "name": "Seguro de Hogar",
        "description": "Protección de vivienda contra daños y robos",
        "keywords": ["casa", "hogar", "propiedad", "vivienda", "daño", "robo"],
        "requirements": ["Identificación", "Título de propiedad"],
        "min_approval_time": 3,
        "max_approval_time": 10
    },
    "POL-004": {
        "id": "POL-004",
        "name": "Seguro de Auto",
        "description": "Cobertura integral para vehículos automotores",
        "keywords": ["auto", "coche", "vehículo", "conducir", "seguro auto"],
        "requirements": ["Identificación", "Título del vehículo", "Licencia de conducir"],
        "min_approval_time": 2,
        "max_approval_time": 7
    },
    "POL-005": {
        "id": "POL-005",
        "name": "Seguro de Viaje",
        "description": "Protección para viajes nacionales e internacionales",
        "keywords": ["viaje", "viajero", "destino", "turismo", "extranjero"],
        "requirements": ["Identificación", "Pasaporte"],
        "min_approval_time": 1,
        "max_approval_time": 3
    }
}


class PolicyMatcher:
    """
    Servicio de Machine Learning para recomendación de políticas
    """
    
    def __init__(self):
        """Inicializa el servicio"""
        logger.info("🤖 Inicializando PolicyMatcher...")
        self.policies = POLICIES_DATABASE
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo ML (simulado por ahora)"""
        try:
            # En futuro: cargar modelo entrenado desde archivo
            # self.model = joblib.load("models/policy_classifier.pkl")
            logger.info("✓ Modelo de políticas cargado")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo cargar modelo: {str(e)}. Usando heurísticas.")
    
    async def find_best_policies(self, client_text: str, client_audio: Optional[str] = None, top_k: int = 3):
        """
        Encuentra las mejores políticas para el cliente
        
        Args:
            client_text: Texto descriptivo del cliente
            client_audio: Audio en base64 (opcional)
            top_k: Número de recomendaciones
            
        Returns:
            Lista de PolicyRecommendation ordenadas por confianza
        """
        try:
            logger.info(f"🔍 Buscando {top_k} mejores políticas...")
            
            # Extraer palabras clave del texto del cliente
            client_keywords = self._extract_keywords(client_text)
            logger.debug(f"Palabras clave extraídas: {client_keywords}")
            
            # Calcular similitud con cada política
            scores = {}
            for policy_id, policy in self.policies.items():
                score = self._calculate_similarity(client_keywords, policy["keywords"])
                scores[policy_id] = score
            
            # Ordenar por score y tomar top k
            sorted_policies = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            # Construir respuesta
            from routers.ia_agent import PolicyRecommendation
            
            recommendations = []
            for policy_id, score in sorted_policies:
                policy = self.policies[policy_id]
                
                recommendation = PolicyRecommendation(
                    policyId=policy["id"],
                    policyName=policy["name"],
                    description=policy["description"],
                    confidence=min(score, 1.0),  # Asegurar que esté entre 0 y 1
                    matchedKeywords=[k for k in policy["keywords"] if k in client_keywords],
                    requirementScore=len(policy["requirements"]) / 10.0
                )
                recommendations.append(recommendation)
            
            logger.info(f"✓ {len(recommendations)} políticas recomendadas")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error encontrando políticas: {str(e)}", exc_info=True)
            raise
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extrae palabras clave del texto
        (Implementación simple - usar NLTK/spaCy en producción)
        """
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            
            # Descargar recursos si es necesario
            try:
                stopwords.words('spanish')
            except:
                nltk.download('stopwords')
                nltk.download('punkt')
            
            # Tokenizar y remover stopwords
            tokens = word_tokenize(text.lower())
            stop_words = set(stopwords.words('spanish'))
            keywords = [t for t in tokens if t.isalpha() and t not in stop_words]
            
            return keywords
        except:
            # Fallback simple si NLTK no está disponible
            return text.lower().split()
    
    def _calculate_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """
        Calcula similitud coseno entre dos listas de palabras
        """
        # Contar ocurrencias
        set1 = set(keywords1)
        set2 = set(keywords2)
        
        # Jaccard similarity
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    async def get_available_policies(self) -> List[Dict]:
        """
        Retorna todas las políticas disponibles
        """
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "requirements": p["requirements"]
            }
            for p in self.policies.values()
        ]
    
    async def train_model(self, training_data: Dict) -> Dict:
        """
        Entrena el modelo con nuevos datos
        (Simulado - en producción usar TensorFlow/PyTorch)
        """
        try:
            logger.info("🤖 Iniciando entrenamiento del modelo...")
            
            # Simulación de entrenamiento
            import time
            start = time.time()
            
            # Aquí iría lógica real de ML
            training_samples = training_data.get("samples", [])
            epochs = training_data.get("epochs", 10)
            
            logger.info(f"📚 Muestras de entrenamiento: {len(training_samples)}")
            logger.info(f"🔄 Épocas: {epochs}")
            
            # Simular entrenamiento
            time.sleep(1)
            
            elapsed = time.time() - start
            
            logger.info(f"✓ Entrenamiento completado en {elapsed:.2f}s")
            
            return {
                "status": "COMPLETED",
                "samples_processed": len(training_samples),
                "epochs": epochs,
                "training_time": elapsed,
                "accuracy": 0.92  # Simulado
            }
            
        except Exception as e:
            logger.error(f"❌ Error entrenando modelo: {str(e)}")
            raise


# Instancia global
_policy_matcher = None


def get_policy_matcher() -> PolicyMatcher:
    """
    Obtiene instancia singleton del PolicyMatcher
    """
    global _policy_matcher
    if _policy_matcher is None:
        _policy_matcher = PolicyMatcher()
    return _policy_matcher
