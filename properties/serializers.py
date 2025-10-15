from rest_framework import serializers
from .models import TipoPropiedad, Propiedad, UbicacionPropiedad, SuperficiePropiedad, SuperficieTerreno, InformacionExtraPropiedad, Ambientes, AmbientePropiedad, ImagenesPropiedad, Servicios, ServicioPropiedad

# echo
class TipoPropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPropiedad
        fields = '__all__'

class PropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propiedad
        fields = '__all__'

# echo
class UbicacionPropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UbicacionPropiedad
        fields = '__all__'
#echo
class SuperficiePropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperficiePropiedad
        fields = '__all__'
#echo
class SuperficieTerrenoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperficieTerreno
        fields = '__all__'
#echo
class InformacionExtraPropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacionExtraPropiedad
        fields = '__all__'
#echo
class AmbientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambientes
        fields = '__all__'

#echo
class AmbientePropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmbientePropiedad
        fields = '__all__'
#ECHO
class ImagenesPropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenesPropiedad
        fields = '__all__'
    
    def validate_imagen(self, value):
        # Validar extensión
        if not value.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise serializers.ValidationError("Solo se permiten archivos PNG y JPG.")
        # Validar tamaño (2MB = 2 * 1024 * 1024 bytes)
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("La imagen no debe pesar más de 2MB.")
        return value
#ECHO
class ServiciosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicios
        fields = '__all__'
#ECHO
class ServicioPropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioPropiedad
        fields = '__all__'

class PrecioPropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propiedad
        fields = ['id', 'precio', 'precio_mantenimiento']