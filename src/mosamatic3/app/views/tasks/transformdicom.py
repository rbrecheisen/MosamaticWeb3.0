from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def transformdicom(request):
    return render(request, 'tasks/transformdicom.html')