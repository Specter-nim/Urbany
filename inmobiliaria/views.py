from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework import viewsets
from .models import Inmobiliaria, UbicacionInmobiliaria
from .serializers import InmobiliariaSerializer, UbicacionInmobiliariaSerializer, RedesSocialesSerializer
from rest_framework.permissions import IsAuthenticated

class InmobiliariaViewSet(viewsets.ModelViewSet):
    queryset = Inmobiliaria.objects.all()
    serializer_class = InmobiliariaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post', 'put'], url_path='redes-sociales')
    def redes_sociales(self, request, pk=None):
        serializer = RedesSocialesSerializer(data=request.data)
        if serializer.is_valid():
            try:
                inmobiliaria = Inmobiliaria.objects.get(id=pk)
            except Inmobiliaria.DoesNotExist:
                return Response({'error': 'Inmobiliaria no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
            for field in ['facebook', 'twitter', 'instagram', 'youtube']:
                if field in serializer.validated_data:
                    setattr(inmobiliaria, field, serializer.validated_data[field])
            inmobiliaria.save()
            return Response({'message': 'Redes sociales actualizadas correctamente.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UbicacionInmobiliariaViewSet(viewsets.ModelViewSet):
    queryset = UbicacionInmobiliaria.objects.all()
    serializer_class = UbicacionInmobiliariaSerializer
    permission_classes = [IsAuthenticated]
