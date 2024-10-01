import os
import sys

from django.core.management import execute_from_command_line


def runserver():
    appPath = os.path.join(os.path.abspath(__file__))
    appPath = os.path.dirname(appPath)
    sys.path.append(appPath)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mosamatic3.settings')
    os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
    os.chdir(appPath)
    print('##############################################################################')
    print('#                   M O S A M A T I C   W E B  3.0                           #')
    print('##############################################################################')
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    execute_from_command_line(['manage.py', 'create_admin_user'])
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])


if __name__ == "__main__":
    runserver()