from django.shortcuts import render
from rest_framework import viewsets
from .models import TipoPropiedad, UbicacionPropiedad, SuperficiePropiedad, SuperficieTerreno, InformacionExtraPropiedad, Ambientes, AmbientePropiedad, ImagenesPropiedad, Servicios, ServicioPropiedad, Propiedad
from .serializers import TipoPropiedadSerializer, UbicacionPropiedadSerializer, SuperficiePropiedadSerializer,  SuperficieTerrenoSerializer, InformacionExtraPropiedadSerializer, AmbientesSerializer, AmbientePropiedadSerializer, ImagenesPropiedadSerializer, ServiciosSerializer, ServicioPropiedadSerializer, PrecioPropiedadSerializer, PropiedadSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets

class TipoPropiedadViewSet(viewsets.ModelViewSet):
    queryset = TipoPropiedad.objects.all()
    serializer_class = TipoPropiedadSerializer
    permission_classes = [IsAuthenticated]

class PropiedadViewSet(viewsets.ModelViewSet):
    queryset = Propiedad.objects.all()
    serializer_class = PropiedadSerializer
    permission_classes = [IsAuthenticated]

class UbicacionPropiedadViewSet(viewsets.ModelViewSet):
    queryset = UbicacionPropiedad.objects.all()
    serializer_class = UbicacionPropiedadSerializer
    permission_classes = [IsAuthenticated]

class SuperficiePropiedadViewSet(viewsets.ModelViewSet):
    queryset = SuperficiePropiedad.objects.all()
    serializer_class = SuperficiePropiedadSerializer
    permission_classes = [IsAuthenticated]

class SuperficieTerrenoViewSet(viewsets.ModelViewSet):
    queryset = SuperficieTerreno.objects.all()
    serializer_class = SuperficieTerrenoSerializer
    permission_classes = [IsAuthenticated]

class InformacionExtraPropiedadViewSet(viewsets.ModelViewSet):
    queryset = InformacionExtraPropiedad.objects.all()
    serializer_class = InformacionExtraPropiedadSerializer
    permission_classes = [IsAuthenticated]

class AmbientesViewSet(viewsets.ModelViewSet):
    queryset = Ambientes.objects.all()
    serializer_class = AmbientesSerializer
    permission_classes = [IsAuthenticated]

class AmbientePropiedadViewSet(viewsets.ModelViewSet):
    queryset = AmbientePropiedad.objects.all()
    serializer_class = AmbientePropiedadSerializer
    permission_classes = [IsAuthenticated]

class ImagenesPropiedadViewSet(viewsets.ModelViewSet):
    queryset = ImagenesPropiedad.objects.all()
    serializer_class = ImagenesPropiedadSerializer
    permission_classes = [IsAuthenticated]

class ServiciosViewSet(viewsets.ModelViewSet):
    queryset = Servicios.objects.all()
    serializer_class = ServiciosSerializer
    permission_classes = [IsAuthenticated]

class ServicioPropiedadViewSet(viewsets.ModelViewSet):
    queryset = ServicioPropiedad.objects.all()
    serializer_class = ServicioPropiedadSerializer
    permission_classes = [IsAuthenticated]

class PrecioPropiedadViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Endpoint para consultar (GET /{pk}/) y actualizar (PUT/PATCH /{pk}/)
    """
    queryset = Propiedad.objects.all()
    serializer_class = PrecioPropiedadSerializer
    permission_classes = [IsAuthenticated]