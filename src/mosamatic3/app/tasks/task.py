from typing import List
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from ..data.datamanager import DataManager
from ..data.logmanager import LogManager
from .taskmanager import TaskManager

LOG = LogManager()


class Task:
    def __init__(self, name: str, display_name: str, description: str, html_page: str, url_pattern: str, task_func, parameter_names: List[str], visible: bool=True) -> None:
        """
        The parent Task constructor requires the following arguments:

        - name              : Fully lower-case name of task (without spaces, e.g., "checkdicomtask"). This name will be used
                              to keep track of the task's status in Redis. For consistency, make this name end in "task"
        - display_name      : Task name to display in the HTML page
        - description       : A one-line description of what the task accomplishes, also displayed in the HTML page
        - html_page         : Name of the HTML page file for this task. It should be "tasks/<task name>.html" where <task name> is equal to task's "name" parameter
        - url_pattern       : The URL pattern for this task's view. Should start with 'tasks/<view name>', so no leading forward slash. The <view name>
                              should be same as the task's "name" parameter.
        - task_func         : The task function object that gets called by the Huey backend when the task needs to execute
        - parameter_names   : The names of any HTML POST parameters that will be passed to the task's view when the form in the HTML page gets submitted.
                              The view will automatically extract these parameters (by their name) and pass them to the task's execution function
        - visible           : Whether this task should be listed in the tasks.html page

        Example task with __init__() constructor:

        class BodyCompositionMetricsTask(Task):
            def __init__(self) -> None:
                super(BodyCompositionMetricsTask, self).__init__(
                    name='bodycompositionmetricstask',
                    display_name='Body composition metrics',
                    description='This task calculates body composition metrics from L3 images and corresponding muscle and fat segmentations',
                    html_page='tasks/bodycompositionmetricstask.html',
                    url_pattern='/tasks/bodycompositionmetricstask',
                    task_func=bodycompositionmetricstask,
                    parameter_names=['fileset_id', 'segmentation_fileset_id', 'output_fileset_name', 'patient_heights_fileset_id'],
                    visible=True,
                )
        """
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
            task_parameters = {'user': request.user} # Always add "user" parameter
            for parameter_name in self.parameter_names: # Iterate through task's HTML POST parameters as specified
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
