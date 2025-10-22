from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Inmobiliaria(models.Model):
    logo = models.ImageField(upload_to='logo_inmobiliaria/', blank=True, null=True)
    nombre = models.CharField(max_length=255)
    telefono = models.CharField('Teléfono', max_length=20, help_text='Teléfono de contacto', blank=True)
    celular = PhoneNumberField('Celular', help_text='Celular de contacto', blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    sitio_web = models.URLField('Sitio Web', blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inmobiliaria"
        verbose_name_plural = "Inmobiliarias"

    def __str__(self):
        return self.nombre 

class UbicacionInmobiliaria(models.Model):
    id_inmobiliaria = models.OneToOneField(Inmobiliaria, on_delete=models.CASCADE, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    departamento = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=255, blank=True)
    distrito = models.CharField(max_length=255, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        verbose_name = "Ubicación de Inmobiliaria"
        verbose_name_plural = "Ubicaciones de Inmobiliarias"

    def __str__(self):
        return f"Ubicación de {self.id_inmobiliaria.nombre}"
