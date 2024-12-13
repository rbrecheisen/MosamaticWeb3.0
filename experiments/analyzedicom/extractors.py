import os
import copy
import json
import pydicom

DATA_DIR = 'D:\\Mosamatic\\Maxime Dewulf Dixon + CT'
DATA_DIR_CT, DATA_DIR_MR = os.path.join(DATA_DIR, 'CT'), os.path.join(DATA_DIR, 'MRI')


class SeriesExtractor:
    def __init__(self, files, modality, image_type_idx=None, image_type_value=None, image_type_idx2=None, image_type_value2=None) -> None:
        self.files = files
        self.modality = modality
        self.image_type_idx = image_type_idx
        self.image_type_value = image_type_value
        self.image_type_idx2 = image_type_idx2
        self.image_type_value2 = image_type_value2

    def run(self):
        series = {self.modality: {}}
        for f in self.files:
            p = pydicom.dcmread(f, stop_before_pixels=True)
            if p.Modality == self.modality:
                if p.PatientID not in series[self.modality].keys():
                    series[self.modality][p.PatientID] = {}
                if p.SeriesInstanceUID not in series[self.modality][p.PatientID].keys():
                    series[self.modality][p.PatientID][p.SeriesInstanceUID] = []
                # Filter by image type if provided
                if self.image_type_idx and self.image_type_value and not self.image_type_idx2 and not self.image_type_value2:
                    if p.ImageType[self.image_type_idx] == self.image_type_value:
                        series[self.modality][p.PatientID][p.SeriesInstanceUID].append(f)
                # Filter by two image types if provided
                if self.image_type_idx and self.image_type_value and self.image_type_idx2 and self.image_type_value2:
                    if p.ImageType[self.image_type_idx] == self.image_type_value and p.ImageType[self.image_type_idx2] == self.image_type_value2:
                        series[self.modality][p.PatientID][p.SeriesInstanceUID].append(f)
                # No image type provided
                else:
                    series[self.modality][p.PatientID][p.SeriesInstanceUID].append(f)
        # Delete empty series by first making a deep copy of the series dictionary and then deleting empty series
        cleared_series = copy.deepcopy(series)
        for patient_id in series[self.modality].keys():
            for series_instance_uid in series[self.modality][patient_id]:
                if len(series[self.modality][patient_id][series_instance_uid]) == 0:
                    del cleared_series[self.modality][patient_id][series_instance_uid]
        return cleared_series


class CtSeriesExtractor(SeriesExtractor):
    def __init__(self, files) -> None:
        super(CtSeriesExtractor, self).__init__(files, modality='CT')


class MrSeriesExtractor(SeriesExtractor):
    def __init__(self, files) -> None:
        super(MrSeriesExtractor, self).__init__(files, modality='MR')


class DixonInPhaseSeriesExtractor(SeriesExtractor):
    def __init__(self, files) -> None:
        super(DixonInPhaseSeriesExtractor, self).__init__(files, modality='MR', image_type_idx=4, image_type_value='IN_PHASE')


class DixonOppositePhaseSeriesExtractor(SeriesExtractor):
    def __init__(self, files) -> None:
        super(DixonOppositePhaseSeriesExtractor, self).__init__(files, modality='MR', image_type_idx=4, image_type_value='OPP_PHASE')


class DixonWaterSeriesExtractor(SeriesExtractor):
    def __init__(self, files) -> None:
        super(DixonWaterSeriesExtractor, self).__init__(files, modality='MR', image_type_idx=4, image_type_value='WATER')


class DwiAdcSeriesExtractor(SeriesExtractor):
    def __init__(self, files) -> None:
        super(DwiAdcSeriesExtractor, self).__init__(files, modality='MR', image_type_idx=2, image_type_value='DIFFUSION', image_type_idx2=3, image_type_value2='ADC')


class DwiBValSeriesExtractor(SeriesExtractor):
    def __init__(self, files) -> None:
        super(DwiBValSeriesExtractor, self).__init__(files, modality='MR', image_type_idx=2, image_type_value='DIFFUSION', image_type_idx2=3, image_type_value2='CALC_BVALUE')


def main():
    files = []
    for f in os.listdir(DATA_DIR_MR):
        files.append(os.path.join(DATA_DIR_MR, f))
    # extractor = DixonInPhaseSeriesExtractor(files)
    # extractor = DixonOppositePhaseSeriesExtractor(files)
    # extractor = DixonWaterSeriesExtractor(files)
    # extractor = DwiAdcSeriesExtractor(files)
    extractor = DwiBValSeriesExtractor(files)
    series = extractor.run()
    print(json.dumps(series, indent=4))


if __name__ == '__main__':
    main()