from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from ...data.datamanager import DataManager


@login_required
def mfal3ct(request):
    action = request.GET.get('action', None)
    if request.method == 'GET':
        manager = DataManager()
        cohorts = manager.get_cohorts()
        if action == 'select-cohort':
            cohort_id = request.GET.get('cohort_id', None)
            selected_cohort = manager.get_cohort(cohort_id)
            patients = manager.get_patients_for_cohort(selected_cohort)
            return render(request, 'tasks/mfal3ct.html', context={'cohorts': cohorts, 'selected_cohort': selected_cohort, 'patients': patients})
        elif action == 'analyze-cohort':
            cohort_id = request.GET.get('cohort_id', None)
            selected_cohort = manager.get_cohort(cohort_id)
            patients = manager.get_patients_for_cohort(selected_cohort)

            # Analyze patients!!

            return render(request, 'tasks/mfal3ct.html', context={'cohorts': cohorts, 'selected_cohort': selected_cohort, 'patients': patients})
        else:
            pass
        return render(request, 'tasks/mfal3ct.html', context={'cohorts': cohorts, 'selected_cohort': None, 'patients': None})
    return HttpResponseForbidden(f'Wrong method ({request.method}) or action ({action})')