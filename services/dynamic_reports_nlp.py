"""
Generador de Reportes Dinámicos con NLP
Permite al usuario describir el reporte que quiere en lenguaje natural
"""
from typing import Dict, List, Any, Optional
import re
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ReportQueryParser:
    """
    Parser NLP para convertir consultas en lenguaje natural a especificaciones de reporte
    """
    
    def __init__(self):
        # Keywords para identificar campos
        self.field_keywords = {
            'politicas': ['política', 'políticas', 'policy', 'policies'],
            'tramites': ['trámite', 'trámites', 'tramite', 'tramites', 'solicitud', 'solicitudes'],
            'usuarios': ['usuario', 'usuarios', 'cliente', 'clientes', 'user', 'users'],
            'estados': ['estado', 'estados', 'status'],
            'departamentos': ['departamento', 'departamentos', 'área', 'áreas'],
            'fechas': ['fecha', 'fechas', 'día', 'días', 'mes', 'meses', 'año', 'años'],
            'documentos': ['documento', 'documentos', 'archivo', 'archivos']
        }
        
        # Keywords para operaciones
        self.operation_keywords = {
            'count': ['cuántos', 'cantidad', 'número', 'total', 'count'],
            'sum': ['suma', 'total', 'acumulado'],
            'average': ['promedio', 'media', 'average'],
            'max': ['máximo', 'mayor', 'max'],
            'min': ['mínimo', 'menor', 'min'],
            'list': ['lista', 'listar', 'mostrar', 'ver', 'list']
        }
        
        # Keywords para filtros
        self.filter_keywords = {
            'estado': {
                'completado': ['completado', 'terminado', 'finalizado', 'completed'],
                'en_proceso': ['proceso', 'en proceso', 'in progress'],
                'rechazado': ['rechazado', 'rejected', 'denegado'],
                'pendiente': ['pendiente', 'pending', 'nuevo']
            },
            'tiempo': {
                'hoy': ['hoy', 'today'],
                'ayer': ['ayer', 'yesterday'],
                'semana': ['semana', 'week'],
                'mes': ['mes', 'month'],
                'año': ['año', 'year']
            }
        }
        
        # Formatos de salida
        self.format_keywords = {
            'excel': ['excel', 'xlsx', 'spreadsheet'],
            'pdf': ['pdf'],
            'word': ['word', 'docx', 'documento'],
            'json': ['json', 'api'],
            'html': ['html', 'web', 'pantalla']
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parsea una consulta en lenguaje natural
        
        Args:
            query: Consulta del usuario, ej: "Quiero ver cuántos trámites completados hay este mes"
        
        Returns:
            Especificación estructurada del reporte
        """
        query_lower = query.lower()
        
        spec = {
            'fields': [],
            'operation': 'list',
            'filters': {},
            'format': 'html',
            'sort_by': None,
            'limit': None,
            'original_query': query
        }
        
        # 1. Detectar campos
        spec['fields'] = self._detect_fields(query_lower)
        
        # 2. Detectar operación
        spec['operation'] = self._detect_operation(query_lower)
        
        # 3. Detectar filtros
        spec['filters'] = self._detect_filters(query_lower)
        
        # 4. Detectar formato
        spec['format'] = self._detect_format(query_lower)
        
        # 5. Detectar ordenamiento
        spec['sort_by'] = self._detect_sorting(query_lower)
        
        # 6. Detectar límite
        spec['limit'] = self._detect_limit(query_lower)
        
        logger.info(f"✓ Query parseado: {spec['operation']} en {spec['fields']} con {len(spec['filters'])} filtros")
        
        return spec
    
    def _detect_fields(self, query: str) -> List[str]:
        """Detecta qué campos se mencionan en la consulta"""
        detected = []
        
        for field, keywords in self.field_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    detected.append(field)
                    break
        
        # Si no detectó nada, asumir trámites por default
        if not detected:
            detected = ['tramites']
        
        return detected
    
    def _detect_operation(self, query: str) -> str:
        """Detecta qué operación quiere el usuario"""
        for operation, keywords in self.operation_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    return operation
        
        return 'list'  # Default
    
    def _detect_filters(self, query: str) -> Dict[str, Any]:
        """Detecta filtros mencionados"""
        filters = {}
        
        # Filtro por estado
        for estado, keywords in self.filter_keywords['estado'].items():
            for keyword in keywords:
                if keyword in query:
                    filters['estado'] = estado
                    break
        
        # Filtro temporal
        for periodo, keywords in self.filter_keywords['tiempo'].items():
            for keyword in keywords:
                if keyword in query:
                    filters['periodo'] = periodo
                    break
        
        # Detectar fechas específicas
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', query)
        if date_match:
            filters['fecha_especifica'] = date_match.group(1)
        
        return filters
    
    def _detect_format(self, query: str) -> str:
        """Detecta formato de salida deseado"""
        for fmt, keywords in self.format_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    return fmt
        
        return 'html'  # Default
    
    def _detect_sorting(self, query: str) -> Optional[str]:
        """Detecta criterio de ordenamiento"""
        if 'ordenado' in query or 'ordenar' in query or 'sort' in query:
            if 'fecha' in query:
                return 'fecha'
            elif 'nombre' in query:
                return 'nombre'
            elif 'estado' in query:
                return 'estado'
        
        return None
    
    def _detect_limit(self, query: str) -> Optional[int]:
        """Detecta límite de resultados"""
        # Buscar números en la consulta
        numbers = re.findall(r'\b(\d+)\b', query)
        
        if numbers:
            # Si dice "top 10" o "primeros 5"
            if 'top' in query or 'primero' in query:
                return int(numbers[0])
        
        return None


class DynamicReportGenerator:
    """
    Generador de reportes dinámicos basado en NLP
    """
    
    def __init__(self):
        self.parser = ReportQueryParser()
    
    def generate_report(self, query: str, data_source: Dict[str, List] = None) -> Dict[str, Any]:
        """
        Genera un reporte a partir de una consulta en lenguaje natural
        
        Args:
            query: Consulta del usuario
            data_source: Datos simulados (en producción vendría de MongoDB)
        
        Returns:
            Reporte estructurado
        """
        # Parsear consulta
        spec = self.parser.parse_query(query)
        
        # Obtener datos (simulados si no se proveen)
        if data_source is None:
            data_source = self._get_simulated_data()
        
        # Aplicar filtros
        filtered_data = self._apply_filters(data_source, spec['filters'])
        
        # Aplicar operación
        result = self._apply_operation(filtered_data, spec['operation'], spec['fields'])
        
        # Aplicar ordenamiento
        if spec['sort_by']:
            result = self._apply_sorting(result, spec['sort_by'])
        
        # Aplicar límite
        if spec['limit'] and isinstance(result, list):
            result = result[:spec['limit']]
        
        # Generar resumen ejecutivo
        summary = self._generate_summary(spec, result, filtered_data)
        
        return {
            'success': True,
            'query': query,
            'specification': spec,
            'data': result,
            'summary': summary,
            'generated_at': datetime.now().isoformat(),
            'format': spec['format']
        }
    
    def _get_simulated_data(self) -> Dict[str, List]:
        """Genera datos simulados para demo"""
        return {
            'tramites': [
                {'id': 'TRM-001', 'estado': 'completado', 'fecha': '2026-06-01', 'politica': 'POL-001'},
                {'id': 'TRM-002', 'estado': 'en_proceso', 'fecha': '2026-06-05', 'politica': 'POL-002'},
                {'id': 'TRM-003', 'estado': 'completado', 'fecha': '2026-06-08', 'politica': 'POL-001'},
                {'id': 'TRM-004', 'estado': 'rechazado', 'fecha': '2026-06-03', 'politica': 'POL-003'},
                {'id': 'TRM-005', 'estado': 'en_proceso', 'fecha': '2026-06-09', 'politica': 'POL-002'},
            ],
            'politicas': [
                {'id': 'POL-001', 'nombre': 'Crédito Bancario', 'activa': True},
                {'id': 'POL-002', 'nombre': 'Instalación Eléctrica', 'activa': True},
                {'id': 'POL-003', 'nombre': 'Soporte Técnico', 'activa': True},
            ]
        }
    
    def _apply_filters(self, data_source: Dict, filters: Dict) -> Dict[str, List]:
        """Aplica filtros a los datos"""
        filtered = {}
        
        for key, items in data_source.items():
            filtered_items = items.copy()
            
            # Filtro por estado
            if 'estado' in filters and key == 'tramites':
                filtered_items = [
                    item for item in filtered_items 
                    if item.get('estado') == filters['estado']
                ]
            
            # Filtro temporal (simplificado)
            if 'periodo' in filters and key == 'tramites':
                # Implementación simplificada
                pass
            
            filtered[key] = filtered_items
        
        return filtered
    
    def _apply_operation(self, data: Dict, operation: str, fields: List[str]) -> Any:
        """Aplica la operación solicitada"""
        # Determinar sobre qué campo trabajar
        primary_field = fields[0] if fields else 'tramites'
        items = data.get(primary_field, [])
        
        if operation == 'count':
            return {'count': len(items), 'entity': primary_field}
        
        elif operation == 'list':
            return items
        
        elif operation == 'sum':
            # Sumar algún valor numérico si existe
            return {'sum': len(items), 'entity': primary_field}
        
        elif operation == 'average':
            return {'average': len(items) / len(data) if data else 0, 'entity': primary_field}
        
        else:
            return items
    
    def _apply_sorting(self, data: Any, sort_by: str) -> Any:
        """Aplica ordenamiento"""
        if isinstance(data, list):
            try:
                return sorted(data, key=lambda x: x.get(sort_by, ''), reverse=True)
            except:
                return data
        return data
    
    def _generate_summary(self, spec: Dict, result: Any, filtered_data: Dict) -> str:
        """Genera resumen ejecutivo del reporte"""
        operation = spec['operation']
        fields = spec['fields'][0] if spec['fields'] else 'items'
        
        if operation == 'count':
            count = result.get('count', 0) if isinstance(result, dict) else len(result) if isinstance(result, list) else 0
            return f"Se encontraron {count} {fields} que cumplen los criterios especificados."
        
        elif operation == 'list':
            count = len(result) if isinstance(result, list) else 0
            return f"Mostrando {count} {fields} según los criterios especificados."
        
        else:
            return f"Reporte generado exitosamente con operación: {operation}"


# Instancia global
report_generator = DynamicReportGenerator()
