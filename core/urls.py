"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication


urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(
        permission_classes=[AllowAny],
        authentication_classes=[SessionAuthentication]
    ), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(
        url_name='schema', 
        permission_classes=[AllowAny],
        authentication_classes=[SessionAuthentication]
    ), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(
        url_name='schema', 
        permission_classes=[AllowAny],
        authentication_classes=[SessionAuthentication]
    ), name='redoc'),
    
    # API endpoints
    path('api/', include('rest_framework.urls')),
    
    # Authentication endpoints
    path('api/auth/', include('authentication.urls')),
    
    # User management endpoints
    path('api/users/', include('users.urls')),
    
    # Role management endpoints
    path('api/roles/', include('roles.urls')),
    
    # Navigation API
    path('api/navegacion/', include('navigation.urls')),
    
    # Activities API
    path('api/actividades/', include('activities.urls')),
    
    # Dashboard
    path('api/dashboard/', include('dashboard.urls')),
    
    # Reports
    path('api/reportes/', include('reports.urls')),
    
    # Alerts
    path('api/alertas/', include('alerts.urls')),
    
    # Contracts
    path('api/contratos/', include('contracts.urls')),
    
    # Messaging
    path('api/mensajes/', include('messaging.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


#En este apartado se colocaran los Endpoints de la API
# path('api/v1/your-app/', include('apps.your_app.urls')),
#!Recordatorio - Los Endpoints se separan por modulo
#!Recordatorio - Los Endpoints se documentan por funciones en un archivo ENDPOINTS.md
#!Recordatorio - Los Endpoints se comentan de igual manera
