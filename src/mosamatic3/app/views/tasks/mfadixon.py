from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def mfadixon(request):
    return render(request, 'tasks/mfadixon.html')