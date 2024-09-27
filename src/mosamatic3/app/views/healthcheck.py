from django.views import View
from django.http import JsonResponse


class HealthCheck(View):
    def get(self, request):
        return JsonResponse({'status': 'ok'})