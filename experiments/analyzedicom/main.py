import os
import pydicom

DATA_DIR = 'D:\\Mosamatic\\Maxime Dewulf Dixon + CT'
DATA_DIR_CT, DATA_DIR_MR = os.path.join(DATA_DIR, 'CT'), os.path.join(DATA_DIR, 'MRI')


def list_modalities(files):
    modalities = []
    for f in files:
        p = pydicom.dcmread(f, stop_before_pixels=True)
        if p.Modality not in modalities:
            modalities.append(p.Modality)
    return modalities


def list_patients(files):
    patient_ids = []
    for f in files:
        p = pydicom.dcmread(f, stop_before_pixels=True)
        if p.PatientID not in patient_ids:
            patient_ids.append(p.PatientID)
    return patient_ids


def list_studies(files):
    study_instance_uids = []
    for f in files:
        p = pydicom.dcmread(f, stop_before_pixels=True)
        if p.StudyInstanceUID not in study_instance_uids:
            study_instance_uids.append(p.StudyInstanceUID)
    return study_instance_uids


def list_series_and_descriptions(files):
    series_instance_uids, series_descriptions = [], []
    for f in files:
        p = pydicom.dcmread(f, stop_before_pixels=True)
        if p.SeriesInstanceUID not in series_instance_uids:
            series_instance_uids.append(p.SeriesInstanceUID)
            if 'SeriesDescription' in p:
                series_descriptions.append(p.SeriesDescription)
            else:
                series_descriptions.append('')
    return series_instance_uids, series_descriptions


def list_image_types(files):
    image_types = []
    for f in files:
        p = pydicom.dcmread(f, stop_before_pixels=True)
        if 'Modality' in p and p.Modality == 'MR':
            if 'ImageType' in p:
                if p.ImageType not in image_types:
                    image_types.append(p.ImageType)
    return image_types


def print_info():
    filenames = os.listdir(DATA_DIR_MR)
    files = []
    for f in filenames:
        files.append(os.path.join(DATA_DIR_MR, f))
    print('= MODALITIES =')
    modalities = list_modalities(files)
    for modality in modalities:
        print(f' - {modality}')
    print()
    print('= PATIENTS =')
    patients = list_patients(files)
    for patient in patients:
        print(f' - {patient}')
    print()
    print('= STUDIES =')
    studies = list_studies(files)
    for study in studies:
        print(f' - {study}')
    print()
    print('= SERIES =')
    series, descriptions = list_series_and_descriptions(files)
    for i in range(len(series)):
        print(f' - {series[i]} ({descriptions[i]})')
    print()
    print('= IMAGE TYPES =')
    image_types = list_image_types(files)
    for image_type in image_types:
        print(f' - {image_type}')


def main():
    print_info()


if __name__ == '__main__':
    main()