import logging
from typing import List
from ..models import LogOutputModel

LOG = logging.getLogger('mosamatic3')


class LogManager:
    def __init__(self) -> None:
        pass

    def info(self, message) -> None:
        LOG.info(message)
        LogOutputModel.objects.create(message=message, mode='info')

    def warning(self, message) -> None:
        LOG.warning(message)
        LogOutputModel.objects.create(message=message, mode='warning')

    def error(self, message) -> None:
        LOG.error(message)
        LogOutputModel.objects.create(message=message, mode='error')

    def get_messages(self) -> List[LogOutputModel]:
        return LogOutputModel.objects.all()
    
    def delete_messages(self):
        for model in LogOutputModel.objects.all():
            model.delete()