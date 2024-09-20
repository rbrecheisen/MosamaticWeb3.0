from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from wsgiref.util import FileWrapper


@login_required
def auth(_):
    return HttpResponse(status=200)


@login_required
def datasets(request):
    return render(request, 'datasets.html', context={'datasets': []})