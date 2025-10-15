from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InmobiliariaViewSet, UbicacionInmobiliariaViewSet

router = DefaultRouter()
router.register(r'inmobiliarias', InmobiliariaViewSet)
router.register(r'ubicaciones', UbicacionInmobiliariaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
