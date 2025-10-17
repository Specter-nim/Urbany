from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

from contacts.models import Contact, Label
from properties.models import Propiedad
from inmobiliaria.models import Inmobiliaria

User = get_user_model()

class Business(models.Model):
    ETAPA_NUEVO = 'NUEVO'
    ETAPA_CONTACTADO = 'CONTACTADO'
    ETAPA_VISITA = 'VISITA_PROGRAMADA'
    ETAPA_NEGOCIACION = 'EN_NEGOCIACION'

    ETAPA_CHOICES = [
        (ETAPA_NUEVO, 'Nuevo negocio'),
        (ETAPA_CONTACTADO, 'Contactado'),
        (ETAPA_VISITA, 'Visita programada'),
        (ETAPA_NEGOCIACION, 'En negociación'),
    ]

    ESTADO_ABIERTO = 'abierto'
    ESTADO_CERRADO = 'cerrado'
    ESTADO_GANADO = 'ganado'

    ESTADO_CHOICES = [
        (ESTADO_ABIERTO, 'Abierto'),
        (ESTADO_CERRADO, 'Cerrado'),
        (ESTADO_GANADO, 'Ganado'),
    ]

    MEDIO_CHOICES = [
        ('FACEBOOK', 'Facebook'),
        ('INSTAGRAM', 'Instagram'),
        ('LINKEDIN', 'LinkedIn'),
        ('WHATSAPP', 'WhatsApp'),
        ('EMAIL', 'Email'),
        ('LLAMADA', 'Llamada'),
        ('REFERIDO', 'Referido'),
        ('OTRO', 'Otro'),
    ]

    contacto = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='negocios')
    propiedad = models.ForeignKey(Propiedad, on_delete=models.SET_NULL, null=True, blank=True, related_name='negocios')
    agente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='negocios')
    #se elimina la inmobiliaria, los negocios asociados se eliminarán también
    inmobiliaria = models.ForeignKey(Inmobiliaria, on_delete=models.CASCADE, related_name='negocios')

    etapa = models.CharField(max_length=32, choices=ETAPA_CHOICES, default=ETAPA_NUEVO)
    estado = models.CharField(max_length=16, choices=ESTADO_CHOICES, default=ESTADO_ABIERTO)
    medio_contacto = models.CharField(max_length=32, choices=MEDIO_CHOICES, blank=True)

    etiquetas = models.ManyToManyField(Label, blank=True, related_name='negocios')

    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(default=timezone.now)
    fecha_etapa = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Negocio'
        verbose_name_plural = 'Negocios'
        ordering = ['-fecha_creacion']
        constraints = [
            # Un negocio abierto por contacto/propiedad
            models.UniqueConstraint(
                fields=['contacto', 'propiedad'],
                condition=Q(estado='abierto'),
                name='unique_open_business_per_contact_property'
            )
        ]

    def __str__(self):
        contacto_nombre = self.contacto.nombre if self.contacto else 'Sin contacto'
        propiedad_id = self.propiedad_id if self.propiedad_id else 'Sin propiedad'
        return f"Negocio de {contacto_nombre} (Propiedad {propiedad_id})"

    @classmethod
    def etapas_en_orden(cls):
        return [
            cls.ETAPA_NUEVO,
            cls.ETAPA_CONTACTADO,
            cls.ETAPA_VISITA,
            cls.ETAPA_NEGOCIACION,
        ]

    def puede_transicionar_a(self, nueva_etapa: str) -> bool:
        orden = self.etapas_en_orden()
        try:
            actual_idx = orden.index(self.etapa)
            nueva_idx = orden.index(nueva_etapa)
        except ValueError:
            return False
        # Solo permitir avanzar exactamente a la siguiente etapa
        return nueva_idx == actual_idx + 1


class BusinessStageHistory(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='historial_etapas')
    etapa_anterior = models.CharField(max_length=32, choices=Business.ETAPA_CHOICES)
    etapa_nueva = models.CharField(max_length=32, choices=Business.ETAPA_CHOICES)
    cambiado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cambios_etapas_negocio')
    fecha_cambio = models.DateTimeField(default=timezone.now)
    nota = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Historial de etapa de negocio'
        verbose_name_plural = 'Historial de etapas de negocio'
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f"{self.business_id}: {self.etapa_anterior} → {self.etapa_nueva} ({self.fecha_cambio})"
