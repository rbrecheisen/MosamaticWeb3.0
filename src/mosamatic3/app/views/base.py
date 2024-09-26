from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required
def auth(_):
    return HttpResponse(status=200)


@login_required
def custom_logout(request):
    logout(request)
    return redirect('/')
