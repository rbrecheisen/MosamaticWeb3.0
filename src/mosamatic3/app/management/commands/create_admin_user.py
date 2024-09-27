from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates admin user'

    def handle(self, *args, **kwargs):
        user = User.objects.filter(username=settings.ADMIN_USER).first()
        if user is None:
            User.objects.create_superuser(
                username=settings.ADMIN_USER, email='', password=settings.ADMIN_PASSWORD, first_name='', last_name='')
            self.stdout.write(self.style.SUCCESS('Successfully created admin user'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin user already exists'))