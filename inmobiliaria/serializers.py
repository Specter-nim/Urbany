from rest_framework import serializers
from .models import Inmobiliaria, UbicacionInmobiliaria

class InmobiliariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inmobiliaria
        fields = '__all__'

    def validate_logo(self, value):
        if value:
            # Validar tamaño
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError("El logo no debe superar los 2MB.")
            # Validar formato
            valid_types = ["image/png", "image/jpeg"]
            if hasattr(value, 'content_type'):
                content_type = value.content_type
            else:
                # fallback para tests o casos sin content_type
                import mimetypes
                content_type, _ = mimetypes.guess_type(value.name)
            if content_type not in valid_types:
                raise serializers.ValidationError("Solo se permiten imágenes PNG o JPG.")
        return value

class UbicacionInmobiliariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UbicacionInmobiliaria
        fields = '__all__'

class RedesSocialesSerializer(serializers.Serializer):
    facebook = serializers.URLField(required=False, allow_blank=True)
    twitter = serializers.URLField(required=False, allow_blank=True)
    instagram = serializers.URLField(required=False, allow_blank=True)
    youtube = serializers.URLField(required=False, allow_blank=True)