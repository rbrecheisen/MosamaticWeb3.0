import pydicom
import pydicom.errors

from ..models import FileModel, PatientCohortModel, PatientModel, DicomStudyModel, DicomSeriesModel, DicomImageModel


class DicomStructureAnalyzer:
    def __init__(self):
        pass

    def get_dicom_object_for_file(self, f):
        try:
            p = pydicom.dcmread(f.path, stop_before_pixels=True)
            return p
        except pydicom.errors.InvalidDicomError as e:
            print(f'DicomStructureAnalyzer.get_dicom_object_for_file() Invalid DICOM object {f.name} (e)')
        return None

    def execute(self, fileset):
        cohort = PatientCohortModel.objects.create(name=f'cohort-{fileset.id}', fileset=fileset)
        files = FileModel.objects.filter(fileset=fileset).all()
        patient_ids = []
        for f in files:
            p = self.get_dicom_object_for_file(f)
            if p:
                patient_id = p.PatientID
                if patient_id not in patient_ids:
                    patient_ids.append(patient_id)
        for patient_id in patient_ids:
            patient = PatientModel.objects.create(name='patient', patient_id=patient_id, cohort=cohort)
            print(f'Created patient-{patient.patient_id}')
            study_instance_uids = []
            for f in files:
                p = self.get_dicom_object_for_file(f)
                if p:
                    study_instance_uid = p.StudyInstanceUID
                    if study_instance_uid not in study_instance_uids:
                        study_instance_uids.append(study_instance_uid)
            for study_instance_uid in study_instance_uids:
                study = DicomStudyModel.objects.create(name='study', study_instance_uid=study_instance_uid, patient=patient)
                print(f'Created study-{study.study_instance_uid} for patient-{patient.patient_id}')
                series_instance_uids = []
                modalities = []
                image_types = []
                for f in files:
                    p = self.get_dicom_object_for_file(f)
                    if p and study_instance_uid == p.StudyInstanceUID:
                        series_instance_uid = p.SeriesInstanceUID
                        if series_instance_uid not in series_instance_uids:
                            series_instance_uids.append(series_instance_uid)
                            modalities.append(p.Modality)
                            image_types.append(p.ImageType)
                for i in range(len(series_instance_uids)):
                    series_instance_uid = series_instance_uids[i]
                    modality = modalities[i]
                    image_type = image_types[i]
                    series = DicomSeriesModel.objects.create(
                        name='series', series_instance_uid=series_instance_uid, modality=modality, image_type=image_type, study=study)
                    print(f'Created series-{series.series_instance_uid} for study-{study.study_instance_uid} and patient-{patient.patient_id}')
                    for f in files:
                        p = self.get_dicom_object_for_file(f)
                        if p and study_instance_uid == p.StudyInstanceUID and series_instance_uid == p.SeriesInstanceUID:
                            instance_uid = p.SOPInstanceUID
                            image = DicomImageModel.objects.create(instance_uid=instance_uid, series=series, file=f)
                            print(f'Created image {image.file.name} for series-{series.series_instance_uid}')