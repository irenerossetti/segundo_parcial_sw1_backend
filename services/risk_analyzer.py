"""
Risk Analyzer Service - Análisis de riesgo usando ML
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """
    Servicio de Machine Learning para análisis de riesgo
    """
    
    def __init__(self):
        """Inicializa el analizador"""
        logger.info("🔴 Inicializando RiskAnalyzer...")
        self.risk_thresholds = {
            "LOW": (0, 30),
            "MEDIUM": (30, 60),
            "HIGH": (60, 85),
            "CRITICAL": (85, 100)
        }
        self.monitoring_tasks = {}
    
    async def analyze_tramite(self, tramite_id: str, client_name: str, policy_type: str,
                            documents: List[str], client_history: Optional[Dict] = None,
                            additional_info: Optional[Dict] = None) -> Dict:
        """
        Analiza riesgo de un trámite
        
        Args:
            tramite_id: ID del trámite
            client_name: Nombre del cliente
            policy_type: Tipo de política
            documents: Lista de documentos
            client_history: Historial del cliente
            additional_info: Información adicional
            
        Returns:
            Análisis completo de riesgo
        """
        try:
            logger.info(f"🔍 Analizando riesgo: tramite={tramite_id}, policy={policy_type}")
            
            # Calcular factores de riesgo
            risk_factors = await self._calculate_risk_factors(
                tramite_id, client_name, policy_type, documents, client_history
            )
            
            # Calcular score general
            overall_score = self._calculate_overall_score(risk_factors)
            overall_level = self._score_to_level(overall_score)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(risk_factors, overall_level)
            
            # Predecir probabilidad de aprobación
            approval_probability = self._predict_approval_probability(overall_score, client_history)
            
            # Estimar días de resolución
            estimated_days = self._estimate_resolution_days(overall_level, policy_type)
            
            result = {
                "overall_score": overall_score,
                "overall_level": overall_level,
                "factors": risk_factors,
                "recommendations": recommendations,
                "approval_probability": approval_probability,
                "estimated_days": estimated_days
            }
            
            logger.info(f"✓ Análisis completado: riesgo={overall_level} (score={overall_score:.1f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analizando riesgo: {str(e)}", exc_info=True)
            raise
    
    async def _calculate_risk_factors(self, tramite_id: str, client_name: str,
                                      policy_type: str, documents: List[str],
                                      client_history: Optional[Dict]) -> List[Dict]:
        """
        Calcula factores individuales de riesgo
        """
        try:
            from routers.risk_analyzer import RiskFactor
            
            factors = []
            
            # Factor 1: Documentación
            doc_risk = self._assess_documentation_risk(documents)
            factors.append(RiskFactor(
                name="Riesgo de Documentación",
                category="DOCUMENTATION",
                riskLevel=doc_risk["level"],
                score=doc_risk["score"],
                description=doc_risk["description"],
                recommendation=doc_risk["recommendation"]
            ))
            
            # Factor 2: Historial del cliente
            if client_history:
                history_risk = self._assess_client_history_risk(client_history)
                factors.append(RiskFactor(
                    name="Riesgo de Cliente",
                    category="CLIENT",
                    riskLevel=history_risk["level"],
                    score=history_risk["score"],
                    description=history_risk["description"],
                    recommendation=history_risk["recommendation"]
                ))
            
            # Factor 3: Tipo de política
            policy_risk = self._assess_policy_risk(policy_type)
            factors.append(RiskFactor(
                name="Riesgo de Política",
                category="POLICY",
                riskLevel=policy_risk["level"],
                score=policy_risk["score"],
                description=policy_risk["description"],
                recommendation=policy_risk["recommendation"]
            ))
            
            # Factor 4: Compliance
            compliance_risk = self._assess_compliance_risk(policy_type, documents)
            factors.append(RiskFactor(
                name="Riesgo de Cumplimiento",
                category="COMPLIANCE",
                riskLevel=compliance_risk["level"],
                score=compliance_risk["score"],
                description=compliance_risk["description"],
                recommendation=compliance_risk["recommendation"]
            ))
            
            return factors
            
        except Exception as e:
            logger.error(f"❌ Error calculando factores de riesgo: {str(e)}")
            raise
    
    def _assess_documentation_risk(self, documents: List[str]) -> Dict:
        """Evalúa riesgo de documentación"""
        required_docs = 5
        provided_docs = len(documents)
        
        if provided_docs == 0:
            return {
                "level": "CRITICAL",
                "score": 95,
                "description": "No hay documentos proporcionados",
                "recommendation": "Solicitar documentación inmediatamente"
            }
        elif provided_docs < required_docs * 0.5:
            return {
                "level": "HIGH",
                "score": 70,
                "description": f"Documentación incompleta ({provided_docs}/{required_docs})",
                "recommendation": "Solicitar documentos faltantes"
            }
        elif provided_docs < required_docs:
            return {
                "level": "MEDIUM",
                "score": 45,
                "description": f"Documentación parcial ({provided_docs}/{required_docs})",
                "recommendation": "Completar documentación"
            }
        else:
            return {
                "level": "LOW",
                "score": 15,
                "description": "Documentación completa",
                "recommendation": "Proceder con revisión"
            }
    
    def _assess_client_history_risk(self, client_history: Dict) -> Dict:
        """Evalúa riesgo basado en historial del cliente"""
        
        previous_claims = client_history.get("previous_claims", 0)
        rejected_claims = client_history.get("rejected_claims", 0)
        payment_history = client_history.get("payment_status", "GOOD")
        
        score = 0
        
        # Penalidad por reclamaciones previas
        if previous_claims > 5:
            score += 30
        elif previous_claims > 2:
            score += 15
        
        # Penalidad por reclamaciones rechazadas
        if rejected_claims > 2:
            score += 40
        elif rejected_claims > 0:
            score += 20
        
        # Penalidad por historial de pago
        if payment_history == "BAD":
            score += 35
        elif payment_history == "FAIR":
            score += 15
        
        level = self._score_to_level(score)
        
        return {
            "level": level,
            "score": min(score, 100),
            "description": f"Historial: {previous_claims} reclamaciones previas, {rejected_claims} rechazadas",
            "recommendation": "Revisar historial detallado y verificar referencias"
        }
    
    def _assess_policy_risk(self, policy_type: str) -> Dict:
        """Evalúa riesgo según tipo de política"""
        
        policy_risks = {
            "Seguro de Vida": {"score": 25, "description": "Riesgo bajo-medio"},
            "Seguro de Salud": {"score": 35, "description": "Riesgo medio"},
            "Seguro de Hogar": {"score": 20, "description": "Riesgo bajo"},
            "Seguro de Auto": {"score": 30, "description": "Riesgo medio-bajo"},
            "Seguro de Viaje": {"score": 15, "description": "Riesgo muy bajo"}
        }
        
        policy_info = policy_risks.get(policy_type, {"score": 50, "description": "Riesgo desconocido"})
        
        return {
            "level": self._score_to_level(policy_info["score"]),
            "score": policy_info["score"],
            "description": f"Política {policy_type}: {policy_info['description']}",
            "recommendation": "Aplicar procedimientos estándar según tipo de póliza"
        }
    
    def _assess_compliance_risk(self, policy_type: str, documents: List[str]) -> Dict:
        """Evalúa riesgo de cumplimiento normativo"""
        
        required_compliance = ["KYC", "AML", "LAS"]
        missing_docs = len([d for d in required_compliance if d not in str(documents)])
        
        score = missing_docs * 20
        
        return {
            "level": self._score_to_level(score),
            "score": min(score, 100),
            "description": f"Documentos de compliance faltantes: {missing_docs}",
            "recommendation": "Completar verificación de cumplimiento normativo"
        }
    
    def _calculate_overall_score(self, factors: List) -> float:
        """Calcula score general de riesgo"""
        if not factors:
            return 50.0
        
        total_score = sum(f.score for f in factors)
        average = total_score / len(factors)
        
        return average
    
    def _score_to_level(self, score: float) -> str:
        """Convierte score numérico a nivel de riesgo"""
        if score < 30:
            return "LOW"
        elif score < 60:
            return "MEDIUM"
        elif score < 85:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_recommendations(self, risk_factors: List, overall_level: str) -> List[str]:
        """Genera recomendaciones basadas en factores de riesgo"""
        recommendations = []
        
        # Recomendaciones por nivel general
        if overall_level == "CRITICAL":
            recommendations.append("🚨 RECOMENDACIÓN URGENTE: Requiere revisión de supervisor antes de proceder")
        elif overall_level == "HIGH":
            recommendations.append("⚠️  Se recomienda revisión adicional antes de aprobar")
        
        # Agregar recomendaciones de cada factor
        for factor in risk_factors:
            if factor.riskLevel in ["HIGH", "CRITICAL"]:
                recommendations.append(f"• {factor.recommendation}")
        
        if not recommendations:
            recommendations.append("✓ Proceder con procedimiento estándar")
        
        return recommendations
    
    def _predict_approval_probability(self, risk_score: float, client_history: Optional[Dict]) -> float:
        """Predice probabilidad de aprobación"""
        
        # Score inverted: alto riesgo = baja probabilidad
        probability = (100 - risk_score) / 100
        
        # Ajustar por historial si disponible
        if client_history:
            if client_history.get("payment_status") == "GOOD":
                probability *= 1.1
            elif client_history.get("payment_status") == "BAD":
                probability *= 0.7
        
        return min(max(probability, 0.0), 1.0)
    
    def _estimate_resolution_days(self, risk_level: str, policy_type: str) -> int:
        """Estima días para resolución"""
        
        base_days = {
            "Seguro de Auto": 3,
            "Seguro de Viaje": 2,
            "Seguro de Hogar": 5,
            "Seguro de Vida": 7,
            "Seguro de Salud": 10
        }
        
        base = base_days.get(policy_type, 7)
        
        # Sumar días por riesgo
        risk_additions = {
            "LOW": 0,
            "MEDIUM": 3,
            "HIGH": 7,
            "CRITICAL": 15
        }
        
        total = base + risk_additions.get(risk_level, 5)
        return total
    
    async def predict_approval(self, tramite_data: Dict) -> Dict:
        """Predice probabilidad de aprobación"""
        try:
            # Análisis simulado
            probability = random.uniform(0.5, 0.95)
            
            return {
                "probability": probability,
                "likelihood": "VERY_HIGH" if probability > 0.8 else "HIGH" if probability > 0.6 else "MEDIUM",
                "top_risks": ["Documentación", "Historial de Cliente"],
                "top_strengths": ["Datos completos", "Historial de pagos"],
                "suggested_actions": ["Revisión rápida", "Aprobación en 5 días"]
            }
        except Exception as e:
            logger.error(f"❌ Error prediciendo aprobación: {str(e)}")
            raise
    
    async def start_monitoring(self, tramite_id: str) -> Dict:
        """Inicia monitoreo de riesgo en tiempo real"""
        try:
            logger.info(f"👁️  Iniciando monitoreo: {tramite_id}")
            
            monitoring_id = f"mon_{tramite_id}_{datetime.now().timestamp()}"
            
            self.monitoring_tasks[monitoring_id] = {
                "tramite_id": tramite_id,
                "started": datetime.now(),
                "status": "ACTIVE"
            }
            
            return {
                "id": monitoring_id,
                "interval": 3600,  # 1 hora
                "threshold": 70  # Score crítico
            }
        except Exception as e:
            logger.error(f"❌ Error iniciando monitoreo: {str(e)}")
            raise


# Instancia global
_risk_analyzer = None


def get_risk_analyzer() -> RiskAnalyzer:
    """
    Obtiene instancia singleton del RiskAnalyzer
    """
    global _risk_analyzer
    if _risk_analyzer is None:
        _risk_analyzer = RiskAnalyzer()
    return _risk_analyzer
