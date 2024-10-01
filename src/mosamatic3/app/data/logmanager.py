from typing import List
from ..models import LogOutputModel


class LogManager:
    def __init__(self) -> None:
        pass

    def info(self, message) -> None:
        LogOutputModel.objects.create(message=message, mode='info')

    def warning(self, message) -> None:
        LogOutputModel.objects.create(message=message, mode='warning')

    def error(self, message) -> None:
        LogOutputModel.objects.create(message=message, mode='error')

    def get_messages(self) -> List[str]:
        messages = []
        for model in LogOutputModel.objects.all():
            messages.append(model.message)
        return messages