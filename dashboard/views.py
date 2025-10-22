from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from .models import DashboardMetric, ChartData, RecentActivity
from .serializers import (
    DashboardMetricSerializer, ChartDataSerializer, RecentActivitySerializer,
    DashboardSummarySerializer, MetricUpdateSerializer, ActivityMarkReadSerializer,
    DashboardStatsSerializer
)


class DashboardSummaryView(APIView):
    """Vista principal del dashboard con todas las métricas, gráficos y actividades"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtiene el resumen completo del dashboard"""
        try:
            # Obtener métricas activas
            metrics = DashboardMetric.objects.filter(is_active=True).order_by('metric_type')
            
            # Obtener actividades recientes (últimas 10)
            recent_activities = RecentActivity.objects.all()[:10]
            
            # Crear objeto dummy para el serializer
            dashboard_data = type('obj', (object,), {})()
            
            serializer = DashboardSummarySerializer(dashboard_data)
            data = serializer.to_representation({
                'metrics': metrics,
                'recent_activities': recent_activities
            })
            
            return Response({
                'success': True,
                'data': data,
                'message': 'Dashboard cargado exitosamente'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al cargar el dashboard'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MetricsListView(generics.ListAPIView):
    """Vista para listar métricas del dashboard"""
    serializer_class = DashboardMetricSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = DashboardMetric.objects.filter(is_active=True)
        
        # Filtros opcionales
        metric_type = self.request.query_params.get('type', None)
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        return queryset.order_by('metric_type', 'name')


class MetricDetailView(generics.RetrieveUpdateAPIView):
    """Vista para obtener y actualizar una métrica específica"""
    queryset = DashboardMetric.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DashboardMetricSerializer
        return MetricUpdateSerializer


class ChartsDataView(generics.ListAPIView):
    """Vista para obtener datos de gráficos del dashboard"""
    serializer_class = ChartDataSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ChartData.objects.filter(is_active=True)
        
        chart_name = self.request.query_params.get('name', None)
        if chart_name:
            queryset = queryset.filter(chart_name=chart_name)
        
        return queryset.order_by('chart_name', 'created_at')


class RecentActivitiesView(generics.ListAPIView):
    """Vista para listar actividades recientes del dashboard"""
    serializer_class = RecentActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RecentActivity.objects.all().order_by('-created_at')


class ActivityMarkReadView(generics.UpdateAPIView):
    """Vista para marcar una actividad del dashboard como leída"""
    queryset = RecentActivity.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ActivityMarkReadSerializer
        return RecentActivitySerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_activities_read(request):
    """Marca todas las actividades recientes como leídas"""
    try:
        RecentActivity.objects.update(is_read=True)
        return Response({
            'success': True,
            'message': 'Todas las actividades marcadas como leídas'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Error al marcar actividades como leídas'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Obtiene estadísticas del dashboard por período"""
    try:
        period = request.query_params.get('period', 'month')
        
        serializer = DashboardStatsSerializer(data={'period': period})
        if serializer.is_valid():
            stats = serializer.to_representation({})
            
            return Response({
                'success': True,
                'data': stats,
                'message': 'Estadísticas obtenidas exitosamente'
            })
        else:
            return Response({
                'success': False,
                'errors': serializer.errors,
                'message': 'Parámetros inválidos'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener estadísticas'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_mock_data(request):
    """Genera datos mock para el dashboard (solo para desarrollo)"""
    try:
        # Generar datos mock
        DashboardMetric.generate_mock_data()
        ChartData.generate_mock_chart_data()
        RecentActivity.generate_mock_activities()
        
        return Response({
            'success': True,
            'message': 'Datos mock generados exitosamente',
            'data': {
                'metrics_created': DashboardMetric.objects.filter(is_active=True).count(),
                'chart_data_created': ChartData.objects.filter(is_active=True).count(),
                'activities_created': RecentActivity.objects.count()
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Error al generar datos mock'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quick_stats(request):
    """Obtiene estadísticas rápidas para widgets del dashboard"""
    try:
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Estadísticas rápidas
        stats = {
            'metrics': {
                'total': DashboardMetric.objects.filter(is_active=True).count(),
                'positive_trend': DashboardMetric.objects.filter(
                    is_active=True, percentage_change__gt=0
                ).count(),
                'negative_trend': DashboardMetric.objects.filter(
                    is_active=True, percentage_change__lt=0
                ).count()
            },
            'activities': {
                'total': RecentActivity.objects.count(),
                'unread': RecentActivity.objects.filter(is_read=False).count(),
                'this_week': RecentActivity.objects.filter(
                    created_at__date__gte=week_ago
                ).count(),
                'this_month': RecentActivity.objects.filter(
                    created_at__date__gte=month_ago
                ).count()
            },
            'charts': {
                'total_charts': ChartData.objects.values('chart_name').distinct().count(),
                'total_data_points': ChartData.objects.filter(is_active=True).count()
            },
            'system': {
                'last_updated': timezone.now(),
                'data_freshness': 'real_time'
            }
        }
        
        return Response({
            'success': True,
            'data': stats,
            'message': 'Estadísticas rápidas obtenidas exitosamente'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener estadísticas rápidas'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardSearchView(APIView):
    """Vista para búsqueda global en el dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Búsqueda global en métricas y actividades"""
        try:
            query = request.query_params.get('q', '').strip()
            
            if not query:
                return Response({
                    'success': False,
                    'message': 'Parámetro de búsqueda requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buscar en métricas
            metrics = DashboardMetric.objects.filter(
                Q(name__icontains=query) | Q(metric_type__icontains=query),
                is_active=True
            )
            
            # Buscar en actividades
            activities = RecentActivity.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )[:10]
            
            # Buscar en gráficos
            charts = ChartData.objects.filter(
                Q(chart_name__icontains=query) | Q(label__icontains=query),
                is_active=True
            )
            
            results = {
                'metrics': DashboardMetricSerializer(metrics, many=True).data,
                'activities': RecentActivitySerializer(activities, many=True).data,
                'charts': ChartDataSerializer(charts, many=True).data,
                'total_results': metrics.count() + activities.count() + charts.count()
            }
            
            return Response({
                'success': True,
                'data': results,
                'query': query,
                'message': f'Se encontraron {results["total_results"]} resultados'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error en la búsqueda'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Endpoint mock estático del dashboard (HU12)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_mock(request):
    """Retorna JSON estático con tres métricas predefinidas"""
    data = {
        'metrics': [
            {
                'name': 'Ventas',
                'value': 120,
                'unit': 'unidades',
                'trend': 'up',
                'change': '+5%'
            },
            {
                'name': 'Propiedades',
                'value': 340,
                'unit': 'listadas',
                'trend': 'down',
                'change': '-2%'
            },
            {
                'name': 'Negocios',
                'value': 48,
                'unit': 'activos',
                'trend': 'flat',
                'change': '0%'
            }
        ],
        'generated_at': timezone.now().isoformat()
    }
    return Response(data)
