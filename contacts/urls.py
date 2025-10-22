from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, LabelViewSet

router = DefaultRouter()
router.register(r'contactos', ContactViewSet)
router.register(r'etiquetas', LabelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]