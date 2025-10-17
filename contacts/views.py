from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, filters, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Contact, Label
from .serializers import ContactSerializer, ContactCreateSerializer, LabelSerializer
import pandas as pd
from django.http import HttpResponse
import io

# Create your views here.
class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [IsAuthenticated]
    
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['tipo', 'agente']
    pagination_class = pagination.PageNumberPagination
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ContactCreateSerializer
        return ContactSerializer
    
    def get_queryset(self):
        queryset = Contact.objects.all()
        
        # Búsqueda unificada por nombre, correo o teléfono
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(correo__icontains=search) | 
                Q(telefono__icontains=search)
            )
        
        # Filtro por agente
        agente_id = self.request.query_params.get('agente', None)
        if agente_id:
            queryset = queryset.filter(agente_id=agente_id)
        
        # Filtro por tipo de contacto
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtro por etiquetas
        etiqueta_id = self.request.query_params.get('etiqueta', None)
        if etiqueta_id:
            queryset = queryset.filter(etiquetas__id=etiqueta_id)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def exportar(self, request):
        queryset = self.get_queryset()
        
        # Obtener el formato de exportación (xlsx o csv)
        formato = request.query_params.get('formato', 'xlsx')
        
        # Crear un DataFrame con los datos
        data = []
        for contact in queryset:
            etiquetas = ", ".join([etiqueta.nombre for etiqueta in contact.etiquetas.all()])
            propiedades = ", ".join([str(propiedad.id) for propiedad in contact.propiedades.all()])
            agente_nombre = f"{contact.agente.first_name} {contact.agente.last_name}".strip() if contact.agente else ""
            
            data.append({
                'ID': contact.id,
                'Nombre': contact.nombre,
                'Correo': contact.correo,
                'Teléfono': contact.telefono,
                'Tipo': contact.tipo,
                'Agente': agente_nombre,
                'Etiquetas': etiquetas,
                'Propiedades': propiedades,
                'Fecha Creación': contact.fecha_creacion,
                'Fecha Actualización': contact.fecha_actualizacion
            })
        
        df = pd.DataFrame(data)
        
        # Crear la respuesta según el formato solicitado
        if formato == 'csv':
            # Exportar como CSV
            output = io.StringIO()
            df.to_csv(output, index=False)
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="contactos.csv"'
        else:
            # Exportar como XLSX (predeterminado)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Contactos', index=False)
            output.seek(0)
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="contactos.xlsx"'
        
        return response
