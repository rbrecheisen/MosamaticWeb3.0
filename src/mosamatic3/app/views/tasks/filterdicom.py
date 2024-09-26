from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def filterdicom(request):
    return render(request, 'tasks/filterdicom.html')