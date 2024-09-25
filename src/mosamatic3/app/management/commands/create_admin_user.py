from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates admin user'

    def handle(self, *args, **kwargs):
        user = User.objects.filter(username='admin').first()
        if user is None:
            User.objects.create_superuser(
                username='admin', email='', password='Arturo4ever', first_name='', last_name='')
            self.stdout.write(self.style.SUCCESS('Successfully created admin user'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin user already exists'))