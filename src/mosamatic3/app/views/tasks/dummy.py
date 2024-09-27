from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import JsonResponse

from ...tasks.dummytask import dummy_task


@login_required
def dummy(request):
    auto_refresh = request.GET.get('auto_refresh', '0')
    action = request.GET.get('action', None)
    if request.method == 'GET':
        if action == 'execute':
            result = dummy_task.delay()
            print(f'task_id: {result.id}')
            return render(request, 'tasks/dummy.html', context={'auto_refresh': auto_refresh})
        else:
            pass
        return render(request, 'tasks/dummy.html', context={'auto_refresh': auto_refresh})
    return HttpResponseForbidden(f'Wrong method ({request.method}) or action ({action})')