from django.contrib import admin
from .models import TipoPropiedad, Propiedad, UbicacionPropiedad, SuperficiePropiedad, SuperficieTerreno, InformacionExtraPropiedad, Ambientes, AmbientePropiedad, ImagenesPropiedad, Servicios, ServicioPropiedad

# Register your models here.
@admin.register(TipoPropiedad)
class TipoPropiedadAdmin(admin.ModelAdmin):
    ordering = ['id']

@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    ordering = ['id']
    readonly_fields = ('fecha_creacion',)

admin.site.register(UbicacionPropiedad)
admin.site.register(SuperficiePropiedad)
admin.site.register(SuperficieTerreno)
admin.site.register(InformacionExtraPropiedad)
admin.site.register(Ambientes)
admin.site.register(AmbientePropiedad)
admin.site.register(ImagenesPropiedad)
admin.site.register(Servicios)
admin.site.register(ServicioPropiedad)

