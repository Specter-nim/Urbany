from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet

router = DefaultRouter()
# Registrar sin prefijo para obtener rutas en /api/negocios/
router.register(r'', BusinessViewSet, basename='negocios')

urlpatterns = [
    path('', include(router.urls)),
]