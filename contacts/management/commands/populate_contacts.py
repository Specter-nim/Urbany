import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
from contacts.models import Contact, Label
from properties.models import Propiedad, TipoPropiedad

User = get_user_model()
fake = Faker('es_ES')  # Usando localizacion española para datos más realistas

class Command(BaseCommand):
    help = 'Popula la base de datos con contactos de prueba'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando datos de prueba para el sistema de contactos...')
        
        # Verificar si hay usuarios en el sistema
        if User.objects.count() == 0:
            self.stdout.write(self.style.WARNING('No hay usuarios en el sistema. Creando un usuario de prueba...'))
            User.objects.create_user(
                email='agente@ejemplo.com',
                password='password123',
                first_name='Agente',
                last_name='Prueba',
                is_active=True
            )
        
        # Obtener usuarios para asignar como agentes
        agentes = User.objects.all()
        
        # Verificar si hay propiedades en el sistema
        propiedades = []
        try:
            propiedades = list(Propiedad.objects.all())
            if not propiedades:
                self.stdout.write(self.style.WARNING('No hay propiedades en el sistema. Los contactos no tendrán propiedades asociadas.'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error al acceder a las propiedades: {str(e)}. Los contactos no tendrán propiedades asociadas.'))
        
        # Crear etiquetas
        etiquetas = [
            'VIP', 'Urgente', 'Seguimiento', 'Nuevo', 'Potencial', 
            'Referido', 'Activo', 'Inactivo', 'Comprador', 'Vendedor',
            'Inversor', 'Extranjero', 'Local'
        ]
        
        etiquetas_obj = []
        for etiqueta in etiquetas:
            obj, created = Label.objects.get_or_create(nombre=etiqueta)
            etiquetas_obj.append(obj)
            if created:
                self.stdout.write(f'Etiqueta creada: {etiqueta}')
            else:
                self.stdout.write(f'Etiqueta existente: {etiqueta}')
        
        # Crear contactos de diferentes tipos
        tipos_contacto = ['interesado', 'propietario', 'otros']
        
        # Crear 20 contactos
        for i in range(20):
            tipo = random.choice(tipos_contacto)
            
            # Crear contacto
            contacto = Contact.objects.create(
                nombre=fake.name(),
                correo=fake.email(),
                telefono=fake.phone_number(),
                tipo=tipo,
                agente=random.choice(agentes) if agentes.exists() else None,
                fecha_creacion=timezone.now(),
                fecha_actualizacion=timezone.now()
            )
            
            # Asignar etiquetas aleatorias (entre 1 y 3)
            num_etiquetas = random.randint(1, 3)
            etiquetas_seleccionadas = random.sample(etiquetas_obj, num_etiquetas)
            contacto.etiquetas.set(etiquetas_seleccionadas)
            
            # Si es propietario, asignar propiedades aleatorias
            if tipo == 'propietario' and propiedades:
                num_propiedades = random.randint(1, min(3, len(propiedades)))
                propiedades_seleccionadas = random.sample(propiedades, num_propiedades)
                # Verificar si existe la relación many-to-many
                if hasattr(contacto, 'propiedades'):
                    contacto.propiedades.set(propiedades_seleccionadas)
                else:
                    self.stdout.write(self.style.WARNING(f'El modelo Contact no tiene una relación many-to-many con Propiedad'))
            
            self.stdout.write(f'Contacto creado: {contacto.nombre} ({contacto.tipo})')
        
        self.stdout.write(self.style.SUCCESS('Datos de prueba creados exitosamente!'))