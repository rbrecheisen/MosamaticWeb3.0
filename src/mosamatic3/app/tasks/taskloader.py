import os
import importlib
import inspect

from typing import List

from .task import Task
from ..data.logmanager import LogManager

LOG = LogManager()


class TaskLoader:
    def run(self) -> List[Task]:
        tasks = []
        tasks_dir = os.path.dirname(__file__)
        for f_name in os.listdir(tasks_dir):
            if f_name.endswith('task.py') and f_name not in ('__init__.py', 'task.py', 'taskloader.py', 'taskexception.py', 'taskmanager.py'):
                module_name = f'.{f_name[:-3]}'
                module = importlib.import_module(module_name, package='app.tasks')
                for _, cls in inspect.getmembers(module, inspect.isclass):
                    if issubclass(cls, Task) and cls is not Task:
                        LOG.info(f'Loading task {f_name}...')
                        tasks.append(cls())
        tasks.sort(key=lambda task: task.display_name)
        return tasks