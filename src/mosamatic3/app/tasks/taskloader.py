import os
import importlib
import inspect

from typing import List

from .task import Task


class TaskLoader:
    def load_task(self, module_name: str) -> Task:
        if not module_name.startswith('.'):
            module_name = f'.{module_name}'
        module = importlib.import_module(module_name, package='app.tasks')
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, Task) and cls is not Task:
                return cls()
        return None

    def run(self) -> List[Task]:
        tasks = []
        tasks_dir = os.path.dirname(__file__)
        for f_name in os.listdir(tasks_dir):
            if f_name.endswith('task.py') and f_name not in ('__init__.py', 'task.py', 'taskloader.py', 'taskexception.py', 'taskmanager.py'):
                module_name = f'.{f_name[:-3]}'
                task = self.load_task(module_name)
                if task:
                    tasks.append(task)
        tasks.sort(key=lambda task: task.display_name)
        return tasks