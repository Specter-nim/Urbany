from django.contrib import admin
from .models import Contact, Label

# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono', 'tipo', 'agente', 'get_etiquetas', 'fecha_creacion')
    list_filter = ('tipo', 'agente', 'etiquetas', 'fecha_creacion')
    search_fields = ('nombre', 'correo', 'telefono')
    filter_horizontal = ('etiquetas', 'propiedades')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def get_etiquetas(self, obj):
        return ", ".join([etiqueta.nombre for etiqueta in obj.etiquetas.all()])
    get_etiquetas.short_description = 'Etiquetas'

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
