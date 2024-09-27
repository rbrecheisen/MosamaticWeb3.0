from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from ...tasks.dummytask import dummy_task


@login_required
def dummy(request):
    auto_refresh = request.GET.get('auto_refresh', '0')
    action = request.GET.get('action', None)
    if request.method == 'GET':
        if action == 'execute':
            print(f'{dummy_task()}')
            return render(request, 'tasks/dummy.html', context={'auto_refresh': auto_refresh})
        else:
            pass
        return render(request, 'tasks/dummy.html', context={'auto_refresh': auto_refresh})
    return HttpResponseForbidden(f'Wrong method ({request.method}) or action ({action})')