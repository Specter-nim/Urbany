from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from properties.models import Propiedad

User = get_user_model()

# Create your models here.
class Label(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"

class Contact(models.Model):
    CONTACT_TYPE_CHOICES = [
        ('interesado', 'Interesado'),
        ('propietario', 'Propietario'),
        ('otro', 'Otro'),
    ]
    
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES)
    agente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contactos')
    propiedades = models.ManyToManyField(Propiedad, blank=True, related_name='contactos')
    etiquetas = models.ManyToManyField(Label, blank=True, related_name='contactos')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.nombre} - {self.tipo}"
    
    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ['-fecha_creacion']

