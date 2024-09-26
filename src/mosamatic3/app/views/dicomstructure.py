from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from ..data.datamanager import DataManager


@login_required
def dicomstructure(request, fileset_id):
    manager = DataManager()
    action = None
    if request.method == 'GET':
        fs = manager.get_fileset(fileset_id)
        cohort = manager.get_cohort_for_fileset(fs)
        action = request.GET.get('action', None)
        if action == 'select-patient':
            patient_id = request.GET.get('patient_id', None)
            selected_patient = manager.get_patient(patient_id)
            patients = manager.get_patients_for_cohort(cohort)
            studies = manager.get_studies_for_patient(selected_patient)
            return render(request, 'dicomstructure.html', context={
                'fileset': fs, 'cohort': cohort, 'patients': patients, 'studies': studies, 'series': [], 'images': [],
                'selected_patient': selected_patient, 'selected_study': None, 'selected_series': None,
            })
        elif action == 'select-study':
            patient_id = request.GET.get('patient_id', None)
            selected_patient = manager.get_patient(patient_id)
            patients = manager.get_patients_for_cohort(cohort)
            study_id = request.GET.get('study_id', None)
            selected_study = manager.get_study(study_id)
            studies = manager.get_studies_for_patient(selected_patient)
            series = manager.get_series_for_study(selected_study)
            return render(request, 'dicomstructure.html', context={
                'fileset': fs, 'cohort': cohort, 'patients': patients, 'studies': studies, 'series': series, 'images': [],
                'selected_patient': selected_patient, 'selected_study': selected_study, 'selected_series': None,
            })
        elif action == 'select-series':
            patient_id = request.GET.get('patient_id', None)
            selected_patient = manager.get_patient(patient_id)
            patients = manager.get_patients_for_cohort(cohort)
            study_id = request.GET.get('study_id', None)
            selected_study = manager.get_study(study_id)
            studies = manager.get_studies_for_patient(selected_patient)
            series_id = request.GET.get('series_id', None)
            selected_series = manager.get_series(series_id)
            series = manager.get_series_for_study(selected_study)
            images = manager.get_images_for_series(selected_series)
            return render(request, 'dicomstructure.html', context={
                'fileset': fs, 'cohort': cohort, 'patients': patients, 'studies': studies, 'series': series, 'images': images,
                'selected_patient': selected_patient, 'selected_study': selected_study, 'selected_series': selected_series,
            })
        else:
            pass
    return HttpResponseForbidden(f'Wrong method ({request.method}) or action ({action})')