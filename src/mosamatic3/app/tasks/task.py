from typing import List
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from .taskmanager import TaskManager

LOG = LogManager()


class Task:
    def __init__(self, name: str, display_name: str, description: str, html_page: str, url_pattern: str, task_func, parameter_names: List[str], visible: bool=True) -> None:
        self.name = name
        self.display_name = display_name
        self.description = description
        self.html_page = html_page
        self.url_pattern = url_pattern
        self.task_func = task_func
        self.parameter_names = parameter_names
        self.visible = visible

    def run(self) -> None:
        raise NotImplementedError('Child tasks must implement this method')

    def view(self, request: HttpRequest) -> HttpResponse:
        data_manager = DataManager()
        task_manager = TaskManager()
        task_model = data_manager.get_task_by_name(self.name)
        if request.method == 'POST':
            task_parameters = {'user': request.user}
            for parameter_name in self.parameter_names:
                task_parameters[parameter_name] = request.POST.get(parameter_name, None)
            return task_manager.run_task_and_get_response(self.task_func, task_parameters)
        elif request.method == 'GET':
            response = task_manager.get_response(self.name, request)
            if response:
                return response
        else:
            pass
        filesets = data_manager.get_filesets(request.user)
        return render(request, task_model.html_page, context={'filesets': filesets, 'task': task_model})
