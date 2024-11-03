from django.core.management.base import BaseCommand

from ...tasks.taskloader import TaskLoader
from ...models import TaskModel


class Command(BaseCommand):
    help = 'Creates tasks'
    def handle(self, *args, **kwargs):
        task_loader = TaskLoader()
        tasks = task_loader.run()
        for task in tasks:
            task_model = TaskModel.objects.filter(name=task.name).first()
            if task_model is None:
                TaskModel.objects.create(
                    name=task.name, display_name=task.display_name, description=task.description, html_page=task.html_page, 
                    url_pattern=task.url_pattern, visible=task.visible)
                message = f'Task {task.name} successfully created'
                self.stdout.write(self.style.SUCCESS(message))
            else:
                task_model.name = task.name
                task_model.display_name = task.display_name
                task_model.description = task.description
                task_model.html_page = task.html_page
                task_model.url_pattern = task.url_pattern
                task_model.visible = task.visible
                task_model.save()
                message = f'Task {task.name} updated'
                self.stdout.write(self.style.SUCCESS(message))