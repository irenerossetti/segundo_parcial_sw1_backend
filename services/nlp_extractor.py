"""
NLP Extractor Service - Procesa texto para extraer requisitos y entidades
Usa NLTK, spaCy y TextBlob para análisis
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NLPExtractor:
    """
    Servicio de NLP para extracción de requisitos y entidades
    """
    
    def __init__(self, language: str = "es"):
        """
        Inicializa el extractor
        
        Args:
            language: Idioma ("es", "en", "fr", "pt")
        """
        logger.info(f"🔤 Inicializando NLPExtractor (language={language})")
        self.language = language
        self._load_models()
    
    def _load_models(self):
        """Carga modelos de NLP"""
        try:
            # Importar librerías NLP
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize, sent_tokenize
            
            # Descargar recursos si es necesario
            try:
                stopwords.words(self.language if self.language == 'spanish' else 'english')
            except:
                logger.info("📥 Descargando recursos NLTK...")
                nltk.download('stopwords')
                nltk.download('punkt')
                nltk.download('averaged_perceptron_tagger')
            
            logger.info("✓ Modelos de NLP cargados")
            
        except Exception as e:
            logger.warning(f"⚠️ Error cargando modelos: {str(e)}")
    
    async def extract_all(self, text: str, extract_entities: bool = True) -> Dict:
        """
        Extrae todo de un texto: requisitos, entidades, resumen
        
        Args:
            text: Texto a procesar
            extract_entities: Si extraer entidades nombradas
            
        Returns:
            Dict con resumen, requisitos, entidades, keywords, sentimiento
        """
        try:
            logger.info(f"🔍 Extrayendo información de texto ({len(text)} caracteres)...")
            
            # Procesar texto
            summary = self._generate_summary(text)
            requirements = await self._extract_requirements(text)
            entities = self._extract_entities(text) if extract_entities else []
            keywords = self._extract_keywords(text)
            sentiment = self._analyze_sentiment(text)
            
            result = {
                "summary": summary,
                "requirements": requirements,
                "entities": entities,
                "keywords": keywords,
                "sentiment": sentiment
            }
            
            logger.info(f"✓ Extracción completada: {len(requirements)} requisitos, {len(entities)} entidades")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo información: {str(e)}", exc_info=True)
            raise
    
    def _generate_summary(self, text: str, num_sentences: int = 3) -> str:
        """
        Genera resumen del texto
        (Implementación simple - en producción usar transformers)
        """
        try:
            from nltk.tokenize import sent_tokenize
            
            sentences = sent_tokenize(text)
            if len(sentences) <= num_sentences:
                return text
            
            # Resumen simple: tomar primeras frases
            summary_sentences = sentences[:num_sentences]
            return " ".join(summary_sentences)
            
        except:
            return text[:500]  # Fallback
    
    async def _extract_requirements(self, text: str) -> List[Dict]:
        """
        Extrae requisitos del texto
        """
        try:
            from routers.nlp_service import ExtractedRequirement
            
            # Palabras clave de requisitos
            requirement_keywords = {
                "DOCUMENTATION": ["documento", "formulario", "certificado", "copia", "original"],
                "PAYMENT": ["pago", "cuota", "precio", "costo", "factura"],
                "APPROVAL": ["aprobación", "aprueba", "autorización", "validación"],
                "TIMELINE": ["días", "semanas", "meses", "plazo", "tiempo"],
                "INSPECTION": ["inspección", "revisión", "verificación", "visita"]
            }
            
            requirements = []
            text_lower = text.lower()
            
            for category, keywords in requirement_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        req = ExtractedRequirement(
                            requirement=f"Requisito de {category.lower()}",
                            category=category,
                            priority="MEDIUM",
                            confidence=0.75
                        )
                        requirements.append(req)
            
            logger.debug(f"Requisitos extraídos: {len(requirements)}")
            return requirements
            
        except Exception as e:
            logger.warning(f"⚠️ Error extrayendo requisitos: {str(e)}")
            return []
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """
        Extrae entidades nombradas (PERSON, ORG, LOCATION, DATE)
        """
        try:
            from routers.nlp_service import ExtractedEntity
            
            # Extracción simple basada en patrones
            entities = []
            
            # Buscar patrones de fecha
            import re
            date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
            for match in re.finditer(date_pattern, text):
                entity = ExtractedEntity(
                    text=match.group(),
                    label="DATE",
                    confidence=0.9,
                    startChar=match.start(),
                    endChar=match.end()
                )
                entities.append(entity)
            
            logger.debug(f"Entidades extraídas: {len(entities)}")
            return entities
            
        except Exception as e:
            logger.warning(f"⚠️ Error extrayendo entidades: {str(e)}")
            return []
    
    def _extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        Extrae palabras clave del texto
        """
        try:
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from collections import Counter
            
            # Tokenizar y limpiar
            tokens = word_tokenize(text.lower())
            stop_words = set(stopwords.words('spanish' if self.language == 'es' else 'english'))
            
            # Filtrar stopwords y palabras cortas
            keywords = [t for t in tokens if t.isalpha() and t not in stop_words and len(t) > 3]
            
            # Contar frecuencias y tomar top k
            counter = Counter(keywords)
            top_keywords = [word for word, count in counter.most_common(top_k)]
            
            logger.debug(f"Keywords extraídas: {top_keywords}")
            return top_keywords
            
        except:
            return []
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Analiza sentimiento del texto
        """
        try:
            from textblob import TextBlob
            
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                return "POSITIVE"
            elif polarity < -0.1:
                return "NEGATIVE"
            else:
                return "NEUTRAL"
                
        except:
            # Fallback: análisis simple por palabras
            positive_words = ["bueno", "excelente", "perfecto", "bien"]
            negative_words = ["malo", "horrible", "problema", "error"]
            
            text_lower = text.lower()
            
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                return "POSITIVE"
            elif neg_count > pos_count:
                return "NEGATIVE"
            else:
                return "NEUTRAL"
    
    async def extract_from_file(self, file_content: bytes, filename: str) -> Dict:
        """
        Extrae información de un archivo
        """
        try:
            logger.info(f"📄 Procesando archivo: {filename}")
            
            # Determinar tipo de archivo
            if filename.endswith('.txt'):
                text = file_content.decode('utf-8')
            elif filename.endswith('.pdf'):
                # En producción: usar PyPDF2 o pdfplumber
                logger.warning("⚠️ Procesamiento PDF no implementado en demo")
                text = "(Contenido PDF - no procesado en demo)"
            else:
                text = file_content.decode('utf-8', errors='ignore')
            
            # Procesar como texto normal
            result = await self.extract_all(text)
            return result
            
        except Exception as e:
            logger.error(f"❌ Error procesando archivo: {str(e)}")
            raise
    
    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similitud entre dos textos
        """
        try:
            from nltk.tokenize import word_tokenize
            
            # Tokenizar
            tokens1 = set(word_tokenize(text1.lower()))
            tokens2 = set(word_tokenize(text2.lower()))
            
            # Jaccard similarity
            intersection = len(tokens1 & tokens2)
            union = len(tokens1 | tokens2)
            
            if union == 0:
                return 0.0
            
            similarity = intersection / union
            logger.debug(f"Similitud entre textos: {similarity:.2f}")
            
            return similarity
            
        except Exception as e:
            logger.error(f"❌ Error calculando similitud: {str(e)}")
            return 0.0


# Instancia global
_nlp_extractor = None


def get_nlp_extractor(language: str = "es") -> NLPExtractor:
    """
    Obtiene instancia singleton del NLPExtractor
    """
    global _nlp_extractor
    if _nlp_extractor is None:
        _nlp_extractor = NLPExtractor(language=language)
    return _nlp_extractor
