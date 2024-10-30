import os
import shutil

ROOT_DIR = 'D:\\Mosamatic\\Nik Pelzer\\L1-L5\\Original\\CT slices 21-06 (post bibi)'
OUTPUT_DIR = 'D:\\Mosamatic\\Nik Pelzer\\L1-L5\\Output'


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for patient_id in os.listdir(ROOT_DIR):
        patient_dir = os.path.join(ROOT_DIR, patient_id)
        if os.path.isdir(patient_dir):
            for f in os.listdir(patient_dir):
                f_path = os.path.join(patient_dir, f)
                if f_path.endswith('.dcm'):
                    patient_id = patient_id.replace(' ', '_')
                    source_dicom_file = f_path
                    target_dicom_file = os.path.join(OUTPUT_DIR, patient_id + '_' + os.path.split(source_dicom_file)[1])
                    source_tag_file = source_dicom_file + '.tag'
                    target_tag_file = os.path.join(OUTPUT_DIR, patient_id + '_' + os.path.split(source_tag_file)[1])
                    shutil.copy(source_dicom_file, target_dicom_file)
                    shutil.copy(source_tag_file, target_tag_file)
                    print(target_tag_file)



if __name__ == '__main__':
    main()