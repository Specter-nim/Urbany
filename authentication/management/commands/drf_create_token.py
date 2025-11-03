from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q


class Command(BaseCommand):
    help = "Genera un token JWT (access y refresh) para un usuario dado"

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nombre de usuario o email del usuario')

    def handle(self, *args, **options):
        username = options['username']
        User = get_user_model()
        user = User.objects.filter(Q(username=username) | Q(email=username)).first()
        if not user:
            raise CommandError(f"Usuario '{username}' no encontrado. Use username o email.")

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        self.stdout.write(self.style.SUCCESS("=== TOKEN GENERADO ==="))
        self.stdout.write(f"Usuario: {user.get_username()}")
        self.stdout.write(f"Access: {str(access)}")
        self.stdout.write(f"Refresh: {str(refresh)}")