from django.urls import path, include
from core.views import ok_view
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, LabelViewSet

router = DefaultRouter()
router.register(r'contactos', ContactViewSet)
# Alias en inglés para compatibilidad de validaciones
router.register(r'contacts', ContactViewSet)
router.register(r'etiquetas', LabelViewSet)

urlpatterns = [
    # Raíz pública de validación
    path('', ok_view, name='contacts-root-ok'),
    path('', include(router.urls)),
]