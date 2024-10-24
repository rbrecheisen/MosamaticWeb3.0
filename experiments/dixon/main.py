import os
import pydicom

DATA_DIR = 'D:\\Mosamatic\\Maxime CT en MRI'
DATA_DIR_CT, DATA_DIR_MR = os.path.join(DATA_DIR, 'CT'), os.path.join(DATA_DIR, 'MRI')


def main():
    for f in os.listdir(DATA_DIR_MR):
        f_path = os.path.join(DATA_DIR_MR, f)
        p = pydicom.dcmread(f_path, stop_before_pixels=True)
        if 'Modality' in p and p.Modality == 'MR':
            if 'ImageType' in p and 'DERIVED' in p.ImageType and p.ImageType[4] in ['IN_PHASE', 'OPP_PHASE', 'WATER']:
                print(f'{f} ImageType: {p.ImageType}, Manufacturer: {p.Manufacturer}')


if __name__ == '__main__':
    main()