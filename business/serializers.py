from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Business, BusinessStageHistory
from contacts.models import Contact, Label
from properties.models import Propiedad
from contacts.serializers import LabelSerializer
from properties.serializers import PropiedadSerializer

User = get_user_model()

class ContactBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'nombre', 'correo', 'telefono']

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class BusinessSerializer(serializers.ModelSerializer):
    contacto_info = ContactBasicSerializer(source='contacto', read_only=True)
    propiedad_info = PropiedadSerializer(source='propiedad', read_only=True)
    etiquetas = LabelSerializer(many=True, read_only=True)

    etiquetas_ids = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='etiquetas'
    )
    propiedad_id = serializers.PrimaryKeyRelatedField(
        queryset=Propiedad.objects.all(),
        write_only=True,
        required=False,
        source='propiedad'
    )

    class Meta:
        model = Business
        fields = [
            'id', 'contacto', 'contacto_info', 'propiedad', 'propiedad_info',
            'agente', 'etapa', 'estado', 'medio_contacto',
            'etiquetas', 'etiquetas_ids',
            'fecha_creacion', 'fecha_actualizacion', 'fecha_etapa',
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'fecha_etapa']

class BusinessCreateSerializer(serializers.ModelSerializer):
    etiquetas_ids = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='etiquetas'
    )

    class Meta:
        model = Business
        fields = [
            'contacto', 'propiedad', 'agente', 'etapa', 'estado', 'medio_contacto', 'etiquetas_ids'
        ]

    def validate(self, attrs):
        contacto = attrs.get('contacto')
        propiedad = attrs.get('propiedad')
        estado = attrs.get('estado', Business.ESTADO_ABIERTO)
        etapa = attrs.get('etapa', Business.ETAPA_NUEVO)

        # Etapa inicial sólo permite NUEVO
        if 'etapa' in attrs and etapa != Business.ETAPA_NUEVO:
            raise serializers.ValidationError({'etapa': 'La etapa inicial debe ser NUEVO.'})

        # Duplicados: negocio abierto por contacto/propiedad
        if estado == Business.ESTADO_ABIERTO and contacto:
            existente = Business.objects.filter(contacto=contacto, propiedad=propiedad, estado=Business.ESTADO_ABIERTO).exists()
            if existente:
                raise serializers.ValidationError({'non_field_errors': 'Ya existe un negocio ABIERTO para este contacto/propiedad.'})
        return attrs

    def create(self, validated_data):
        etiquetas = validated_data.pop('etiquetas', [])
        negocio = Business.objects.create(**validated_data)
        if etiquetas:
            negocio.etiquetas.set(etiquetas)
        # fecha_etapa inicial
        negocio.fecha_etapa = timezone.now()
        negocio.fecha_actualizacion = timezone.now()
        negocio.save()
        return negocio

class BusinessImportSerializer(serializers.Serializer):
    file = serializers.FileField()
    agente = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    etiquetas_ids = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all(), many=True, required=False)
    column_map = serializers.DictField(child=serializers.CharField(), required=False)

    def validate_column_map(self, value):
        # Asegurar claves mínimas
        expected = {'nombre', 'telefono', 'email'}
        if value:
            missing = expected - set(value.keys())
            if missing:
                raise serializers.ValidationError(f"Faltan columnas requeridas: {', '.join(missing)}")
        return value

class BusinessStageUpdateSerializer(serializers.Serializer):
    etapa = serializers.ChoiceField(choices=Business.ETAPA_CHOICES)
    nota = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        business: Business = self.context['business']
        nueva = attrs['etapa']
        if not business.puede_transicionar_a(nueva):
            raise serializers.ValidationError({'etapa': 'Transición de etapa no permitida (debe ser secuencial).'})
        return attrs