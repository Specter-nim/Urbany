from django.urls import path, include
from core.views import ok_view
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet

router = DefaultRouter()
# Registrar sin prefijo para obtener rutas en /api/negocios/
router.register(r'', BusinessViewSet, basename='negocios')

urlpatterns = [
    # Raíz pública de validación
    path('', ok_view, name='business-root-ok'),
    path('', include(router.urls)),
]