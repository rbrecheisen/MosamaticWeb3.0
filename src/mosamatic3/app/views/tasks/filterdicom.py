from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def filterdicom(request):
    if request.method == 'GET':
        action = request.GET.get('action', None)
        if action == 'execute':
            pass
    return render(request, 'tasks/filterdicom.html')