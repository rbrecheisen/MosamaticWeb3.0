import logging

from typing import List
from django.db import connection
from django.db.utils import OperationalError
from django.apps import apps

from ..models import LogOutputModel

LOG = logging.getLogger('mosamatic3')


class LogManager:
    def __init__(self) -> None:
        self.db_exists = False

    def write_to_db(self, message, mode):
        # Only write to database if table (data model) exists
        try:
            model = apps.get_model('app', 'LogOutputModel')
            table_name = model._meta.db_table
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1 FROM information_schema.tables WHERE table_name=%s', [table_name])
                if cursor.fetchone():
                    self.db_exists = True
        except OperationalError:
            self.db_exists = False
        if self.db_exists:
            LogOutputModel.objects.create(message=message, mode=mode)

    def info(self, message) -> None:
        LOG.info(message)
        self.write_to_db(message, 'info')

    def warning(self, message) -> None:
        LOG.warning(message)
        self.write_to_db(message, 'warning')

    def error(self, message) -> None:
        LOG.error(message)
        self.write_to_db(message, 'error')

    def get_messages(self) -> List[LogOutputModel]:
        return LogOutputModel.objects.all()
    
    def delete_messages(self):
        for model in LogOutputModel.objects.all():
            model.delete()