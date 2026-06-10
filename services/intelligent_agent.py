"""
Agente Inteligente para Asignación Automática de Políticas
Reemplaza al punto de atención humano
"""
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import json


class IntelligentPolicyAgent:
    """
    Agente inteligente que:
    1. Escucha requerimientos del cliente (texto/voz)
    2. Determina la política de negocio más apropiada
    3. Identifica requisitos necesarios
    4. Valida documentación antes de asignar
    """
    
    def __init__(self):
        # Keywords por categoría de política
        self.policy_keywords = {
            "INSTALACION_ELECTRICA": {
                "keywords": ["eléctrica", "electricidad", "instalación", "luz", "medidor", "cfe", "cre"],
                "requires_docs": ["identificación", "comprobante domicilio", "título propiedad"],
                "priority_default": "MEDIA"
            },
            "CREDITO_BANCARIO": {
                "keywords": ["crédito", "préstamo", "financiamiento", "banco", "dinero", "solicitud"],
                "requires_docs": ["identificación", "comprobante ingresos", "estado cuenta"],
                "priority_default": "ALTA"
            },
            "RECLUTAMIENTO": {
                "keywords": ["trabajo", "empleo", "vacante", "reclutamiento", "contratar", "cv"],
                "requires_docs": ["cv", "identificación", "referencias", "certificados"],
                "priority_default": "MEDIA"
            },
            "COMPRAS": {
                "keywords": ["compra", "adquisición", "proveedor", "cotización", "orden"],
                "requires_docs": ["cotización", "autorización", "requisición"],
                "priority_default": "BAJA"
            },
            "SOPORTE_TECNICO": {
                "keywords": ["soporte", "técnico", "problema", "falla", "error", "sistema"],
                "requires_docs": ["descripción problema", "capturas pantalla"],
                "priority_default": "ALTA"
            },
            "VACACIONES": {
                "keywords": ["vacaciones", "descanso", "ausencia", "permiso"],
                "requires_docs": ["solicitud vacaciones"],
                "priority_default": "BAJA"
            }
        }
    
    def analyze_client_request(self, text: str, audio_transcript: Optional[str] = None) -> Dict[str, Any]:
        """
        Analiza la solicitud del cliente y determina:
        - Política apropiada
        - Nivel de confianza
        - Requisitos necesarios
        - Prioridad sugerida
        """
        # Combinar texto y transcripción si existe
        full_text = f"{text} {audio_transcript or ''}".lower()
        
        # Calcular scores por categoría
        scores = {}
        for category, config in self.policy_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in config["keywords"]:
                if keyword in full_text:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                scores[category] = {
                    "score": score,
                    "confidence": min(score / len(config["keywords"]) * 100, 95),
                    "matched_keywords": matched_keywords,
                    "required_docs": config["requires_docs"],
                    "priority": config["priority_default"]
                }
        
        # Ordenar por score
        sorted_policies = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        if not sorted_policies:
            return {
                "success": False,
                "message": "No se pudo identificar una política adecuada. Por favor proporciona más detalles.",
                "suggestions": [
                    "¿Necesitas realizar una instalación?",
                    "¿Buscas solicitar un crédito?",
                    "¿Requieres soporte técnico?",
                    "¿Quieres solicitar vacaciones?"
                ]
            }
        
        # Mejor coincidencia
        best_match = sorted_policies[0]
        category = best_match[0]
        details = best_match[1]
        
        # Alternativas (si hay otras con score cercano)
        alternatives = []
        for alt_cat, alt_details in sorted_policies[1:3]:
            if alt_details["score"] >= details["score"] * 0.6:  # 60% del mejor
                alternatives.append({
                    "category": alt_cat,
                    "confidence": alt_details["confidence"],
                    "reason": f"Detecté {len(alt_details['matched_keywords'])} palabras relacionadas"
                })
        
        return {
            "success": True,
            "recommended_policy": {
                "category": category,
                "confidence": details["confidence"],
                "matched_keywords": details["matched_keywords"],
                "required_documents": details["required_docs"],
                "priority": details["priority"]
            },
            "alternatives": alternatives,
            "reasoning": f"Identifiqué {details['score']} términos clave relacionados con {category.replace('_', ' ').title()}",
            "next_steps": [
                f"Prepara los siguientes documentos: {', '.join(details['required_docs'])}",
                "Revisa los requisitos específicos de la política",
                "Confirma que deseas iniciar este trámite"
            ]
        }
    
    def validate_requirements(self, category: str, provided_docs: List[str]) -> Dict[str, Any]:
        """
        Valida si el cliente tiene los documentos necesarios
        """
        if category not in self.policy_keywords:
            return {"valid": False, "message": "Categoría de política no reconocida"}
        
        required = set(self.policy_keywords[category]["requires_docs"])
        provided = set(doc.lower() for doc in provided_docs)
        
        missing = required - provided
        extra = provided - required
        
        is_valid = len(missing) == 0
        
        return {
            "valid": is_valid,
            "required_docs": list(required),
            "provided_docs": list(provided),
            "missing_docs": list(missing),
            "extra_docs": list(extra),
            "completion_percentage": (len(provided & required) / len(required)) * 100 if required else 100,
            "message": "Todos los documentos requeridos están presentes" if is_valid else f"Faltan: {', '.join(missing)}"
        }
    
    def suggest_priority(self, text: str, urgency_keywords: List[str] = None) -> str:
        """
        Sugiere prioridad basada en palabras clave de urgencia
        """
        if urgency_keywords is None:
            urgency_keywords = ["urgente", "inmediato", "prioritario", "emergencia", "crítico", "ya"]
        
        text_lower = text.lower()
        
        for keyword in urgency_keywords:
            if keyword in text_lower:
                return "ALTA"
        
        return "MEDIA"
    
    def generate_conversation_response(self, stage: str, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Genera respuestas conversacionales según la etapa del proceso
        """
        responses = {
            "greeting": {
                "text": "¡Hola! Soy tu asistente inteligente. ¿En qué puedo ayudarte hoy?",
                "suggestions": [
                    "Necesito solicitar un servicio",
                    "Quiero hacer un trámite",
                    "Tengo una consulta"
                ]
            },
            "analyzing": {
                "text": f"Entiendo que necesitas {context.get('category', 'realizar un trámite')}. Déjame verificar los requisitos...",
                "suggestions": []
            },
            "policy_found": {
                "text": f"Perfecto. He identificado que necesitas la política de {context.get('policy_name', 'trámite')} con {context.get('confidence', 0)}% de confianza.",
                "suggestions": [
                    "Continuar con este trámite",
                    "Ver requisitos",
                    "Buscar otra política"
                ]
            },
            "missing_docs": {
                "text": f"Para continuar, necesito que subas los siguientes documentos: {', '.join(context.get('missing', []))}",
                "suggestions": [
                    "Subir documentos ahora",
                    "Continuar sin documentos",
                    "Cancelar"
                ]
            },
            "ready_to_start": {
                "text": "¡Excelente! Tienes todos los requisitos. ¿Deseas iniciar el trámite ahora?",
                "suggestions": [
                    "Sí, iniciar trámite",
                    "Revisar información",
                    "Cancelar"
                ]
            }
        }
        
        return responses.get(stage, {
            "text": "¿Hay algo más en lo que pueda ayudarte?",
            "suggestions": []
        })


class ConversationManager:
    """
    Maneja el flujo conversacional completo con el cliente
    """
    
    def __init__(self):
        self.agent = IntelligentPolicyAgent()
        self.conversations = {}  # user_id -> conversation_state
    
    def start_conversation(self, user_id: str) -> Dict[str, Any]:
        """Inicia una nueva conversación"""
        self.conversations[user_id] = {
            "stage": "greeting",
            "history": [],
            "context": {},
            "started_at": datetime.now().isoformat()
        }
        
        response = self.agent.generate_conversation_response("greeting", {})
        
        return {
            "conversation_id": user_id,
            "response": response,
            "stage": "greeting"
        }
    
    def process_message(self, user_id: str, message: str, audio_transcript: Optional[str] = None) -> Dict[str, Any]:
        """
        Procesa un mensaje del usuario y retorna respuesta apropiada
        """
        if user_id not in self.conversations:
            self.start_conversation(user_id)
        
        conv = self.conversations[user_id]
        conv["history"].append({
            "role": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        current_stage = conv["stage"]
        
        # Analizar intención
        if current_stage == "greeting":
            # Analizar solicitud del cliente
            analysis = self.agent.analyze_client_request(message, audio_transcript)
            
            if analysis["success"]:
                conv["context"]["analysis"] = analysis
                conv["stage"] = "policy_found"
                
                response = {
                    "text": f"Entiendo. Detecté que necesitas: **{analysis['recommended_policy']['category'].replace('_', ' ').title()}** (Confianza: {analysis['recommended_policy']['confidence']:.0f}%)\n\n"
                            f"📋 Requisitos necesarios:\n" + "\n".join(f"• {doc}" for doc in analysis['recommended_policy']['required_documents']),
                    "suggestions": [
                        "Continuar con esta política",
                        "Ver alternativas",
                        "Explicar más detalles"
                    ]
                }
            else:
                response = {
                    "text": analysis["message"],
                    "suggestions": analysis.get("suggestions", [])
                }
        
        elif current_stage == "policy_found":
            if "continuar" in message.lower() or "sí" in message.lower() or "si" in message.lower():
                conv["stage"] = "checking_docs"
                response = {
                    "text": "Perfecto. ¿Ya cuentas con los documentos necesarios?",
                    "suggestions": [
                        "Sí, tengo todo",
                        "No, ¿cuáles necesito?",
                        "Subir documentos"
                    ]
                }
            elif "alternativa" in message.lower():
                analysis = conv["context"].get("analysis", {})
                alternatives = analysis.get("alternatives", [])
                
                if alternatives:
                    alt_text = "\n".join(
                        f"• {alt['category'].replace('_', ' ').title()} ({alt['confidence']:.0f}%)"
                        for alt in alternatives
                    )
                    response = {
                        "text": f"Otras opciones detectadas:\n{alt_text}\n\n¿Cuál prefieres?",
                        "suggestions": [alt['category'] for alt in alternatives]
                    }
                else:
                    response = {
                        "text": "No encontré alternativas cercanas. ¿Puedes darme más detalles de lo que necesitas?",
                        "suggestions": []
                    }
            else:
                response = {
                    "text": "¿Deseas continuar con la política sugerida o necesitas algo más?",
                    "suggestions": ["Continuar", "Cambiar política", "Cancelar"]
                }
        
        elif current_stage == "checking_docs":
            if "sí" in message.lower() or "si" in message.lower() or "tengo" in message.lower():
                conv["stage"] = "ready_to_start"
                response = self.agent.generate_conversation_response("ready_to_start", {})
            else:
                analysis = conv["context"].get("analysis", {})
                docs = analysis.get("recommended_policy", {}).get("required_documents", [])
                response = {
                    "text": f"Necesitarás:\n" + "\n".join(f"• {doc}" for doc in docs) + "\n\n¿Deseas subirlos ahora?",
                    "suggestions": ["Subir ahora", "Continuar sin documentos", "Cancelar"]
                }
        
        elif current_stage == "ready_to_start":
            if "sí" in message.lower() or "si" in message.lower() or "iniciar" in message.lower():
                # Aquí se crearía el trámite real
                analysis = conv["context"].get("analysis", {})
                policy = analysis.get("recommended_policy", {})
                
                response = {
                    "text": f"✅ ¡Trámite iniciado exitosamente!\n\n"
                            f"📋 Política: {policy.get('category', 'N/A').replace('_', ' ').title()}\n"
                            f"🎯 Prioridad: {policy.get('priority', 'MEDIA')}\n"
                            f"📊 Confianza: {policy.get('confidence', 0):.0f}%\n\n"
                            f"Recibirás notificaciones sobre el progreso de tu trámite.",
                    "suggestions": [],
                    "action": "create_tramite",
                    "data": {
                        "policy_category": policy.get("category"),
                        "priority": policy.get("priority"),
                        "confidence": policy.get("confidence"),
                        "required_docs": policy.get("required_documents", [])
                    }
                }
                
                conv["stage"] = "completed"
            else:
                response = {
                    "text": "¿Qué te gustaría hacer?",
                    "suggestions": ["Iniciar trámite", "Revisar información", "Cancelar"]
                }
        
        else:
            response = {
                "text": "¿Puedo ayudarte con algo más?",
                "suggestions": ["Nuevo trámite", "Consultar estado", "Salir"]
            }
        
        conv["history"].append({
            "role": "assistant",
            "message": response["text"],
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "conversation_id": user_id,
            "response": response,
            "stage": conv["stage"],
            "context": conv["context"]
        }
    
    def get_conversation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene el historial de conversación"""
        if user_id not in self.conversations:
            return []
        return self.conversations[user_id]["history"]


# Instancia global
conversation_manager = ConversationManager()
