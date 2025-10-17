from rest_framework import serializers
from .models import Contact, Label
from properties.models import Propiedad
from properties.serializers import PropiedadSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'nombre']

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class ContactSerializer(serializers.ModelSerializer):
    etiquetas = LabelSerializer(many=True, read_only=True)
    etiquetas_ids = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.all(), 
        many=True, 
        write_only=True,
        required=False,
        source='etiquetas'
    )
    propiedades_info = PropiedadSerializer(source='propiedades', many=True, read_only=True)
    propiedades_ids = serializers.PrimaryKeyRelatedField(
        queryset=Propiedad.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='propiedades'
    )
    agente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            'id', 'nombre', 'correo', 'telefono', 'tipo', 
            'agente', 'agente_nombre', 'etiquetas', 'etiquetas_ids',
            'propiedades_info', 'propiedades_ids',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']

    def get_agente_nombre(self, obj):
        if obj.agente:
            return f"{obj.agente.first_name} {obj.agente.last_name}".strip() or obj.agente.email
        return None

class ContactCreateSerializer(serializers.ModelSerializer):
    etiquetas_ids = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.all(), 
        many=True, 
        write_only=True,
        required=False,
        source='etiquetas'
    )
    propiedades_ids = serializers.PrimaryKeyRelatedField(
        queryset=Propiedad.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='propiedades'
    )

    class Meta:
        model = Contact
        fields = [
            'id', 'nombre', 'correo', 'telefono', 'tipo', 
            'agente', 'etiquetas_ids', 'propiedades_ids'
        ]

    def validate(self, data):
        tipo = data.get('tipo')
        propiedades = data.get('propiedades', [])
        
        # Validación específica para propietarios - hacemos opcional la asociación
        # para permitir crear propietarios sin propiedades inicialmente
        # if tipo == 'propietario' and not propiedades:
        #     raise serializers.ValidationError(
        #         {"propiedades_ids": "Un propietario debe tener al menos una propiedad asociada."}
        #     )
            
        return data