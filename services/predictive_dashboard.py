"""
Dashboard Predictivo Avanzado
Métricas, análisis y predicciones visuales para el workflow
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
import logging

logger = logging.getLogger(__name__)


class PredictiveDashboardService:
    """
    Servicio de dashboard con analíticas predictivas
    """
    
    def __init__(self):
        # Simular datos históricos
        self.historical_data = self._generate_historical_data()
    
    def _generate_historical_data(self, days: int = 90) -> List[Dict]:
        """Genera datos históricos simulados"""
        np.random.seed(42)
        
        data = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            # Simular patrones realistas
            weekday = date.weekday()
            is_weekend = weekday >= 5
            
            # Menos trámites en fin de semana
            base_count = 15 if not is_weekend else 5
            
            # Tendencia creciente
            trend = i * 0.1
            
            # Estacionalidad semanal
            seasonal = 5 * np.sin(2 * np.pi * weekday / 7)
            
            # Ruido
            noise = np.random.normal(0, 3)
            
            tramites_count = max(0, int(base_count + trend + seasonal + noise))
            
            # Estados distribuidos
            total = tramites_count
            completados = int(total * 0.4)
            en_proceso = int(total * 0.35)
            rechazados = int(total * 0.15)
            pendientes = total - completados - en_proceso - rechazados
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'tramites_total': tramites_count,
                'completados': completados,
                'en_proceso': en_proceso,
                'rechazados': rechazados,
                'pendientes': pendientes,
                'tiempo_promedio_dias': np.random.uniform(3, 15),
                'satisfaccion': np.random.uniform(3.5, 5.0)
            })
        
        return data
    
    def get_overview_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas generales del dashboard
        """
        recent = self.historical_data[-30:]  # Últimos 30 días
        previous = self.historical_data[-60:-30]  # 30 días anteriores
        
        # Calcular totales
        total_tramites = sum(d['tramites_total'] for d in recent)
        total_completados = sum(d['completados'] for d in recent)
        total_rechazados = sum(d['rechazados'] for d in recent)
        total_en_proceso = sum(d['en_proceso'] for d in recent)
        
        # Calcular cambios vs periodo anterior
        prev_total = sum(d['tramites_total'] for d in previous)
        cambio_tramites = ((total_tramites - prev_total) / prev_total * 100) if prev_total > 0 else 0
        
        prev_completados = sum(d['completados'] for d in previous)
        cambio_completados = ((total_completados - prev_completados) / prev_completados * 100) if prev_completados > 0 else 0
        
        # Promedios
        avg_tiempo = np.mean([d['tiempo_promedio_dias'] for d in recent])
        avg_satisfaccion = np.mean([d['satisfaccion'] for d in recent])
        
        # Tasa de éxito
        tasa_exito = (total_completados / total_tramites * 100) if total_tramites > 0 else 0
        
        return {
            'periodo': '30 días',
            'total_tramites': total_tramites,
            'cambio_tramites_porcentaje': round(cambio_tramites, 1),
            'total_completados': total_completados,
            'cambio_completados_porcentaje': round(cambio_completados, 1),
            'total_rechazados': total_rechazados,
            'total_en_proceso': total_en_proceso,
            'tasa_exito_porcentaje': round(tasa_exito, 1),
            'tiempo_promedio_dias': round(avg_tiempo, 1),
            'satisfaccion_promedio': round(avg_satisfaccion, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_time_series(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtiene serie temporal de trámites
        """
        recent = self.historical_data[-days:]
        
        dates = [d['date'] for d in recent]
        tramites = [d['tramites_total'] for d in recent]
        completados = [d['completados'] for d in recent]
        rechazados = [d['rechazados'] for d in recent]
        en_proceso = [d['en_proceso'] for d in recent]
        
        return {
            'labels': dates,
            'datasets': [
                {
                    'label': 'Total Trámites',
                    'data': tramites,
                    'color': '#3498db'
                },
                {
                    'label': 'Completados',
                    'data': completados,
                    'color': '#27ae60'
                },
                {
                    'label': 'En Proceso',
                    'data': en_proceso,
                    'color': '#f39c12'
                },
                {
                    'label': 'Rechazados',
                    'data': rechazados,
                    'color': '#e74c3c'
                }
            ]
        }
    
    def get_predictions(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Genera predicciones para próximos días
        """
        # Obtener últimos 14 días
        recent = self.historical_data[-14:]
        recent_counts = [d['tramites_total'] for d in recent]
        
        # Predecir usando promedio móvil simple + tendencia
        window = 7
        moving_avg = np.mean(recent_counts[-window:])
        
        # Calcular tendencia
        x = np.arange(len(recent_counts))
        y = np.array(recent_counts)
        z = np.polyfit(x, y, 1)
        trend = z[0]
        
        # Generar predicciones
        predictions = []
        for i in range(days_ahead):
            pred = moving_avg + (trend * i)
            pred = max(0, pred + np.random.normal(0, 2))  # Agregar variabilidad
            predictions.append(round(pred, 1))
        
        # Generar fechas futuras
        last_date = datetime.strptime(self.historical_data[-1]['date'], '%Y-%m-%d')
        future_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') 
                       for i in range(days_ahead)]
        
        # Calcular banda de confianza
        std_dev = np.std(recent_counts)
        confidence_upper = [p + std_dev for p in predictions]
        confidence_lower = [max(0, p - std_dev) for p in predictions]
        
        return {
            'dates': future_dates,
            'predictions': predictions,
            'confidence': {
                'upper': confidence_upper,
                'lower': confidence_lower
            },
            'trend': 'creciente' if trend > 0 else 'decreciente',
            'confidence_level': 0.68  # 1 desviación estándar ≈ 68%
        }
    
    def get_distribution_by_state(self) -> Dict[str, Any]:
        """
        Distribución de trámites por estado
        """
        recent = self.historical_data[-30:]
        
        total_completados = sum(d['completados'] for d in recent)
        total_en_proceso = sum(d['en_proceso'] for d in recent)
        total_rechazados = sum(d['rechazados'] for d in recent)
        total_pendientes = sum(d['pendientes'] for d in recent)
        
        total = total_completados + total_en_proceso + total_rechazados + total_pendientes
        
        return {
            'labels': ['Completados', 'En Proceso', 'Rechazados', 'Pendientes'],
            'data': [total_completados, total_en_proceso, total_rechazados, total_pendientes],
            'percentages': [
                round(total_completados / total * 100, 1) if total > 0 else 0,
                round(total_en_proceso / total * 100, 1) if total > 0 else 0,
                round(total_rechazados / total * 100, 1) if total > 0 else 0,
                round(total_pendientes / total * 100, 1) if total > 0 else 0
            ],
            'colors': ['#27ae60', '#f39c12', '#e74c3c', '#95a5a6']
        }
    
    def get_processing_time_analysis(self) -> Dict[str, Any]:
        """
        Análisis de tiempos de procesamiento
        """
        recent = self.historical_data[-30:]
        times = [d['tiempo_promedio_dias'] for d in recent]
        
        return {
            'promedio': round(np.mean(times), 1),
            'mediana': round(np.median(times), 1),
            'minimo': round(min(times), 1),
            'maximo': round(max(times), 1),
            'desviacion_estandar': round(np.std(times), 1),
            'distribucion': {
                'rapido': len([t for t in times if t < 5]),
                'normal': len([t for t in times if 5 <= t < 10]),
                'lento': len([t for t in times if t >= 10])
            },
            'tendencia': 'mejorando' if times[-7:] < times[-14:-7] else 'empeorando'
        }
    
    def get_satisfaction_trend(self) -> Dict[str, Any]:
        """
        Tendencia de satisfacción de usuarios
        """
        recent = self.historical_data[-30:]
        
        dates = [d['date'] for d in recent]
        satisfaction = [d['satisfaccion'] for d in recent]
        
        # Calcular promedio móvil de 7 días
        window = 7
        moving_avg = []
        for i in range(len(satisfaction)):
            if i < window:
                moving_avg.append(np.mean(satisfaction[:i+1]))
            else:
                moving_avg.append(np.mean(satisfaction[i-window+1:i+1]))
        
        return {
            'labels': dates,
            'data': satisfaction,
            'moving_average': moving_avg,
            'promedio_actual': round(np.mean(satisfaction[-7:]), 2),
            'cambio_vs_anterior': round(
                np.mean(satisfaction[-7:]) - np.mean(satisfaction[-14:-7]), 2
            )
        }
    
    def get_bottleneck_alerts(self) -> List[Dict[str, Any]]:
        """
        Detecta alertas de cuellos de botella
        """
        recent = self.historical_data[-7:]
        
        alerts = []
        
        # Alert 1: Alto volumen en proceso
        en_proceso_total = sum(d['en_proceso'] for d in recent)
        if en_proceso_total > 100:
            alerts.append({
                'level': 'warning',
                'title': 'Alto volumen en proceso',
                'message': f'{en_proceso_total} trámites en proceso en últimos 7 días',
                'recommendation': 'Asignar más recursos al procesamiento'
            })
        
        # Alert 2: Tasa de rechazo alta
        total_recent = sum(d['tramites_total'] for d in recent)
        rechazados_recent = sum(d['rechazados'] for d in recent)
        tasa_rechazo = (rechazados_recent / total_recent * 100) if total_recent > 0 else 0
        
        if tasa_rechazo > 20:
            alerts.append({
                'level': 'danger',
                'title': 'Tasa de rechazo elevada',
                'message': f'{round(tasa_rechazo, 1)}% de trámites rechazados',
                'recommendation': 'Revisar criterios de validación y capacitar personal'
            })
        
        # Alert 3: Tiempo de procesamiento aumentando
        times_recent = [d['tiempo_promedio_dias'] for d in recent]
        if len(times_recent) > 3:
            if times_recent[-1] > times_recent[0] * 1.3:
                alerts.append({
                    'level': 'warning',
                    'title': 'Tiempo de procesamiento aumentando',
                    'message': f'Aumento del {round((times_recent[-1]/times_recent[0] - 1) * 100, 1)}%',
                    'recommendation': 'Identificar cuellos de botella en el workflow'
                })
        
        # Si no hay alertas
        if not alerts:
            alerts.append({
                'level': 'success',
                'title': 'Todo bajo control',
                'message': 'No se detectaron anomalías en las métricas',
                'recommendation': 'Continuar con el monitoreo rutinario'
            })
        
        return alerts
    
    def get_top_performers(self) -> Dict[str, Any]:
        """
        Usuarios/departamentos con mejor desempeño
        """
        # Datos simulados de usuarios
        performers = [
            {'name': 'María González', 'tramites_procesados': 145, 'tasa_exito': 94.5, 'tiempo_promedio': 4.2},
            {'name': 'Carlos Rodríguez', 'tramites_procesados': 132, 'tasa_exito': 91.2, 'tiempo_promedio': 5.1},
            {'name': 'Ana Martínez', 'tramites_procesados': 128, 'tasa_exito': 93.8, 'tiempo_promedio': 4.8},
            {'name': 'Luis Hernández', 'tramites_procesados': 119, 'tasa_exito': 89.7, 'tiempo_promedio': 5.9},
            {'name': 'Sofia López', 'tramites_procesados': 115, 'tasa_exito': 92.1, 'tiempo_promedio': 5.3}
        ]
        
        return {
            'top_performers': performers,
            'criterio': 'Trámites procesados últimos 30 días'
        }


# Instancia global
predictive_dashboard = PredictiveDashboardService()
