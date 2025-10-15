from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from inmobiliaria.models import Inmobiliaria

class TipoPropiedad(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Tipo de Propiedad"
        verbose_name_plural = "Tipos de Propiedades"

    def __str__(self):
        return f"{self.nombre}"
    
class Propiedad(models.Model):
    OPERACION_CHOICES = [
        ('venta', 'Venta'),
        ('alquiler', 'Alquiler'),
        ('alquiler_temporal', 'Alquiler Temporal'),
    ]
    
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('reservada', 'Reservada'),
        ('fuera de mercado', 'Fuera de Mercado'),
        ('vendida', 'Vendida'),
        ('alquilada', 'Alquilada'),
        ('en borrador', 'En Borrador'),
    ]
    
    id_inmobiliaria = models.ForeignKey(Inmobiliaria, on_delete=models.CASCADE)
    tipo_propiedad = models.ForeignKey(TipoPropiedad, on_delete=models.CASCADE)
    #propietario = models.ForeignKey(Contacto, on_delete=models.CASCADE, blank=True, null=True)
    tipo_operacion = models.CharField(max_length=20, choices=OPERACION_CHOICES)
    amoblado = models.BooleanField(default=False)
    permuta = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    sitio_web = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    es_borrador = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    publicada = models.BooleanField(default=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    precio_mantenimiento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Propiedad"
        verbose_name_plural = "Propiedades"

    def __str__(self):
        return f"Propiedad {self.id} - {self.tipo_propiedad.nombre} - Inmobiliaria: {self.id_inmobiliaria.nombre}"
    
class UbicacionPropiedad(models.Model):
    id_propiedad = models.OneToOneField(Propiedad, on_delete=models.CASCADE, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    departamento = models.CharField(max_length=255, blank=True)
    provincia = models.CharField(max_length=255, blank=True)
    distrito = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Ubicación de Propiedad"
        verbose_name_plural = "Ubicaciones de Propiedades"

    def __str__(self):
        return f"Ubicación {self.id_propiedad.id}"

#para tipos de propiedades como casas, departamentos, oficinas, etc.
class SuperficiePropiedad(models.Model):
    id_propiedad = models.OneToOneField(Propiedad, on_delete=models.CASCADE)
    area_techada = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    area_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    area_descubierta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    area_terreno = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    area_semicubierta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Superficie de Propiedad"
        verbose_name_plural = "Superficies de Propiedades"

    def __str__(self):
        return f"Superficie {self.area_total} - Propiedad {self.id_propiedad.id}"

#para tipos de propiedades como campos, terrenos, fincas , etc.
class SuperficieTerreno(models.Model):
    FORMAS_CHOICES = [
        ('regular', 'Regular'),
        ('irregular', 'Irregular'),
    ]

    id_propiedad = models.OneToOneField(Propiedad, on_delete=models.CASCADE)
    metros_frente = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    metros_fondo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    area_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    area_construible = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    forma_terreno = models.CharField(max_length=20, choices=FORMAS_CHOICES, blank=True)

    class Meta:
        verbose_name = "Superficie de Terreno"
        verbose_name_plural = "Superficies de Terrenos"

    def __str__(self):
        return f"Superficie {self.area_total} - Propiedad {self.id_propiedad.id}"


class InformacionExtraPropiedad(models.Model):
    ANTIGUEDAD_FORMS = [
        ('a estrenar', 'A estrenar'),
        ('en construccion', 'En construcción'),
        ('otro', 'Otro'),
    ]

    ORIENTACION_CHOICES = [
        ('norte', 'Norte'),
        ('sur', 'Sur'),
        ('este', 'Este'),
        ('oeste', 'Oeste'),
        ('noreste', 'Noreste'),
        ('noroeste', 'Noroeste'),
        ('sureste', 'Sureste'),
        ('suroeste', 'Suroeste'),
    ]

    id_propiedad = models.OneToOneField(Propiedad, on_delete=models.CASCADE)
    antiguedad = models.CharField(max_length=20, choices=ANTIGUEDAD_FORMS, blank=True)
    años_antiguedad = models.PositiveIntegerField(blank=True, null=True)
    orientacion = models.CharField(max_length=20, choices=ORIENTACION_CHOICES, blank=True)
    descripcion_adicional = models.TextField(blank=True)

    def clean(self):
        if self.antiguedad == 'otro' and self.años_antiguedad is None:
            raise ValidationError({'años_antiguedad': 'Debes ingresar los años de antigüedad si seleccionas "otro".'})
        if self.antiguedad != 'otro' and self.años_antiguedad is not None:
            raise ValidationError({'años_antiguedad': 'Solo puedes ingresar años de antigüedad si seleccionas "otro".'})
    
    class Meta:
        verbose_name = "Información Extra de Propiedad"
        verbose_name_plural = "Información Extra de Propiedades"
    
    def __str__(self):
        return f"Información Extra {self.id_propiedad.id}"

class Ambientes(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Ambiente"
        verbose_name_plural = "Ambientes"

    def __str__(self):
        return self.nombre

class AmbientePropiedad(models.Model): 
    id_propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    id_ambiente = models.ForeignKey(Ambientes, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Ambiente de Propiedad"
        verbose_name_plural = "Ambientes de Propiedades"
        unique_together = ('id_propiedad', 'id_ambiente')

    def __str__(self):
        return f"Ambiente: {self.id_ambiente.nombre} - Propiedad: {self.id_propiedad.id}"

class ImagenesPropiedad(models.Model):
    id_propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='imagenes_propiedades/')

    def save(self, *args, **kwargs):
        if ImagenesPropiedad.objects.filter(id_propiedad=self.id_propiedad).count() >= 30 and not self.pk:
            raise ValidationError("No se pueden subir más de 30 imágenes para esta propiedad.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Imagen de Propiedad"
        verbose_name_plural = "Imágenes de Propiedades"

    def __str__(self):
        return f"Imagen de Propiedad {self.id_propiedad.id}"

class Servicios(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.nombre

class ServicioPropiedad(models.Model):
    id_propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    id_servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Servicio de Propiedad"
        verbose_name_plural = "Servicios de Propiedades"

    def __str__(self):
        return f"Servicio: {self.id_servicio.nombre} - Propiedad: {self.id_propiedad.id}"