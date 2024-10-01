from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest


@login_required
def auth(_) -> HttpResponse:
    return HttpResponse(status=200)


@login_required
def custom_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('/')
