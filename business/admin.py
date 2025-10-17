from django.contrib import admin
from django.utils import timezone
from .models import Business, BusinessStageHistory

class BusinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'contacto', 'propiedad', 'etapa', 'estado', 'agente', 'fecha_creacion')
    list_filter = ('etapa', 'estado', 'agente', 'etiquetas')
    search_fields = ('contacto__nombre', 'contacto__correo', 'contacto__telefono', 'propiedad__id')
    actions = ['marcar_contactado', 'marcar_visita', 'marcar_negociacion']

    def _mass_change_etapa(self, request, queryset, nueva_etapa, label):
        cambios = 0
        for negocio in queryset:
            if negocio.puede_transicionar_a(nueva_etapa):
                anterior = negocio.etapa
                negocio.etapa = nueva_etapa
                negocio.fecha_etapa = timezone.now()
                negocio.fecha_actualizacion = timezone.now()
                negocio.save()
                BusinessStageHistory.objects.create(
                    business=negocio,
                    etapa_anterior=anterior,
                    etapa_nueva=nueva_etapa,
                    cambiado_por=request.user if request.user.is_authenticated else None,
                    fecha_cambio=timezone.now(),
                    nota=f"Cambio masivo desde admin: {label}",
                )
                cambios += 1
        self.message_user(request, f"{cambios} negocios actualizados a {label}.")

    def marcar_contactado(self, request, queryset):
        self._mass_change_etapa(request, queryset, Business.ETAPA_CONTACTADO, 'CONTACTADO')
    marcar_contactado.short_description = 'Cambiar etapa a CONTACTADO'

    def marcar_visita(self, request, queryset):
        self._mass_change_etapa(request, queryset, Business.ETAPA_VISITA, 'VISITA_PROGRAMADA')
    marcar_visita.short_description = 'Cambiar etapa a VISITA_PROGRAMADA'

    def marcar_negociacion(self, request, queryset):
        self._mass_change_etapa(request, queryset, Business.ETAPA_NEGOCIACION, 'EN_NEGOCIACION')
    marcar_negociacion.short_description = 'Cambiar etapa a EN_NEGOCIACION'

class BusinessStageHistoryAdmin(admin.ModelAdmin):
    list_display = ('business', 'etapa_anterior', 'etapa_nueva', 'cambiado_por', 'fecha_cambio')
    list_filter = ('etapa_anterior', 'etapa_nueva', 'cambiado_por')
    search_fields = ('business__id', 'business__contacto__nombre')

admin.site.register(Business, BusinessAdmin)
admin.site.register(BusinessStageHistory, BusinessStageHistoryAdmin)
