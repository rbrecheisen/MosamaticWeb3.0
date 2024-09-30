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
    print('#                               H U E Y                                      #')
    print('##############################################################################')
    execute_from_command_line(['manage.py', 'run_huey'])


if __name__ == "__main__":
    runserver()