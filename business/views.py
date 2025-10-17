from django.db.models import Q, Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Business, BusinessStageHistory
from .serializers import (
    BusinessSerializer,
    BusinessCreateSerializer,
    BusinessImportSerializer,
    BusinessStageUpdateSerializer,
)

import csv
import io
from datetime import timedelta
from contacts.models import Contact, Label
from django.contrib.auth import get_user_model

User = get_user_model()

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.select_related('contacto', 'propiedad', 'agente').prefetch_related('etiquetas')
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = pagination.PageNumberPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BusinessCreateSerializer
        return BusinessSerializer

    def get_queryset(self):
        queryset = Business.objects.select_related('contacto', 'propiedad', 'agente').prefetch_related('etiquetas')
        params = self.request.query_params

        # Búsqueda unificada por nombre, email, teléfono y algunos datos de propiedad
        search = params.get('search')
        if search:
            q = (
                Q(contacto__nombre__icontains=search)
                | Q(contacto__correo__icontains=search)
                | Q(contacto__telefono__icontains=search)
            )
            # búsqueda por ID de propiedad si es numérico
            if search.isdigit():
                q = q | Q(propiedad__id=int(search))
            else:
                q = q | Q(propiedad__tipo_propiedad__nombre__icontains=search)
            queryset = queryset.filter(q)

        # Filtro por agente
        agente_id = params.get('agente')
        if agente_id:
            queryset = queryset.filter(agente_id=agente_id)

        # Filtro por etapa
        etapa = params.get('etapa')
        if etapa:
            queryset = queryset.filter(etapa=etapa)

        # Filtro por estado
        estado = params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        # Filtro por etiqueta
        etiqueta_id = params.get('etiqueta')
        if etiqueta_id:
            queryset = queryset.filter(etiquetas__id=etiqueta_id)

        # Filtro por propiedad
        propiedad_id = params.get('propiedad')
        if propiedad_id:
            queryset = queryset.filter(propiedad_id=propiedad_id)

        return queryset.distinct()

    @action(detail=True, methods=['post'], url_path='cambiar-etapa')
    def cambiar_etapa(self, request, pk=None):
        business = self.get_object()
        serializer = BusinessStageUpdateSerializer(data=request.data, context={'business': business})
        serializer.is_valid(raise_exception=True)
        nueva_etapa = serializer.validated_data['etapa']
        nota = serializer.validated_data.get('nota', '')

        anterior = business.etapa
        business.etapa = nueva_etapa
        business.fecha_etapa = timezone.now()
        business.fecha_actualizacion = timezone.now()
        business.save()

        BusinessStageHistory.objects.create(
            business=business,
            etapa_anterior=anterior,
            etapa_nueva=nueva_etapa,
            cambiado_por=request.user if request.user.is_authenticated else None,
            fecha_cambio=timezone.now(),
            nota=nota,
        )

        return Response(BusinessSerializer(business).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='importar')
    def importar_csv(self, request):
        serializer = BusinessImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        agente = serializer.validated_data.get('agente') or (request.user if request.user.is_authenticated else None)
        etiquetas_ids = serializer.validated_data.get('etiquetas_ids', [])
        column_map = serializer.validated_data.get('column_map') or {
            'nombre': 'nombre',
            'telefono': 'telefono',
            'email': 'email',
        }

        etiquetas = list(Label.objects.filter(id__in=etiquetas_ids)) if etiquetas_ids else []

        # Leer CSV
        try:
            # Intentar detectar encoding
            raw = file.read()
            text = raw.decode('utf-8', errors='ignore')
            stream = io.StringIO(text)
            reader = csv.DictReader(stream)
        except Exception as e:
            return Response({'detail': f'Error al leer CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        creados = 0
        duplicados = 0
        errores = []

        for idx, row in enumerate(reader, start=1):
            try:
                nombre = row.get(column_map['nombre'])
                telefono = row.get(column_map['telefono'])
                email = row.get(column_map['email'])

                if not (nombre or email or telefono):
                    errores.append({'fila': idx, 'error': 'Faltan datos mínimos (nombre/email/teléfono)'})
                    continue

                # Buscar o crear contacto
                contacto = None
                if email:
                    contacto = Contact.objects.filter(correo=email).first()
                if not contacto and telefono:
                    contacto = Contact.objects.filter(telefono=telefono).first()
                if not contacto:
                    contacto = Contact.objects.create(
                        nombre=nombre or (email or telefono),
                        correo=email or '',
                        telefono=telefono or '',
                        tipo='interesado',
                        agente=agente if isinstance(agente, User) else None,
                        fecha_creacion=timezone.now(),
                        fecha_actualizacion=timezone.now(),
                    )

                # Evitar duplicados abiertos por contacto/propiedad (aquí propiedad None)
                existe_abierto = Business.objects.filter(contacto=contacto, propiedad=None, estado=Business.ESTADO_ABIERTO).exists()
                if existe_abierto:
                    duplicados += 1
                    continue

                negocio = Business.objects.create(
                    contacto=contacto,
                    propiedad=None,
                    agente=agente if isinstance(agente, User) else None,
                    etapa=Business.ETAPA_NUEVO,
                    estado=Business.ESTADO_ABIERTO,
                    medio_contacto='OTRO',
                    fecha_creacion=timezone.now(),
                    fecha_actualizacion=timezone.now(),
                    fecha_etapa=timezone.now(),
                )
                if etiquetas:
                    negocio.etiquetas.set(etiquetas)

                creados += 1
            except Exception as e:
                errores.append({'fila': idx, 'error': str(e)})

        return Response({
            'creados': creados,
            'duplicados': duplicados,
            'errores': errores,
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        qs = self.get_queryset()

        # Conteo por etapa
        por_etapa = list(
            qs.values('etapa').annotate(total=Count('id')).order_by('etapa')
        )

        # Totales por estado
        total_abiertos = qs.filter(estado=Business.ESTADO_ABIERTO).count()
        total_cerrados = qs.filter(estado=Business.ESTADO_CERRADO).count()
        total_ganados = qs.filter(estado=Business.ESTADO_GANADO).count()

        # Evolución temporal (últimos 30 días)
        desde = timezone.now() - timedelta(days=30)
        evolucion_qs = (
            qs.filter(fecha_creacion__gte=desde)
              .annotate(dia=TruncDay('fecha_creacion'))
              .values('dia')
              .annotate(total=Count('id'))
              .order_by('dia')
        )
        evolucion = [
            {'fecha': e['dia'].date().isoformat(), 'total': e['total']}
            for e in evolucion_qs
        ]

        return Response({
            'por_etapa': por_etapa,
            'totales': {
                'abiertos': total_abiertos,
                'cerrados': total_cerrados,
                'ganados': total_ganados,
            },
            'evolucion_30_dias': evolucion,
        })
