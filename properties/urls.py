from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipoPropiedadViewSet, UbicacionPropiedadViewSet, SuperficiePropiedadViewSet, SuperficieTerrenoViewSet, InformacionExtraPropiedadViewSet, AmbientesViewSet, AmbientePropiedadViewSet, ImagenesPropiedadViewSet, ServiciosViewSet, PrecioPropiedadViewSet, ServicioPropiedadViewSet, PropiedadViewSet

router = DefaultRouter()
router.register(r'tipo-propiedad', TipoPropiedadViewSet, basename='tipo-propiedad')
router.register(r'ubicacion-propiedad', UbicacionPropiedadViewSet, basename='ubicacion-propiedad')
router.register(r'superficie-propiedad', SuperficiePropiedadViewSet, basename='superficie-propiedad')
router.register(r'superficie-terreno', SuperficieTerrenoViewSet, basename='superficie-terreno')
router.register(r'informacion-extra-propiedad', InformacionExtraPropiedadViewSet, basename='informacion-extra-propiedad')
router.register(r'ambientes', AmbientesViewSet, basename='ambientes')
router.register(r'ambiente-propiedad', AmbientePropiedadViewSet, basename='ambiente-propiedad')
router.register(r'imagenes-propiedad', ImagenesPropiedadViewSet, basename='imagenes-propiedad')
router.register(r'servicios', ServiciosViewSet, basename='servicios')
router.register(r'precio-propiedad', PrecioPropiedadViewSet, basename='precio-propiedad')
router.register(r'servicio-propiedad', ServicioPropiedadViewSet, basename='servicio-propiedad')
router.register(r'propiedad', PropiedadViewSet, basename='propiedad')

urlpatterns = [
    path('', include(router.urls)),
]

