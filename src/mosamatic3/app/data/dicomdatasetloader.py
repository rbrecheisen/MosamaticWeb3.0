"""
DicomDataSetLoader

Directory structure:
/datasets
/datasets/<dataset_id>
/datasets/<dataset_id>/<fileset_id>
/datasets/<dataset_id>/<fileset_id>/<file_id>

This hierarchy should support most datasets. A single CT scan will be a FileSet with its individual images
the File objects. A Dixon MRI scan will also be a FileSet object but all of its images (including in-phase,
out-of-phase, water and fat images) will be stored as one long list of File objects. The post-processing
functionality should figure out which images correspond to the water and fat images.

A FileSet object corresponds to a DICOM series. For Dixon MRI there will be multiple series per patient
corresponding to the in-phase, out-of-phase, water and fat images. These will all be stored underneath the
DataSet object.
"""
import pydicom
import pydicom.errors

from pydicom.uid import ExplicitVRLittleEndian, ImplicitVRLittleEndian, ExplicitVRBigEndian

from .datasetloader import DataSetLoader
from ..models import DataSetModel, FileSetModel, FileModel


class DicomDataSetLoader(DataSetLoader):
    def __init__(self) -> None:
        pass

    def is_compressed(self, p):
        return p.file_meta.TransferSyntaxUID not in [ExplicitVRLittleEndian, ImplicitVRLittleEndian, ExplicitVRBigEndian]

    def load(self, file_paths, file_names, user=None) -> None:

        if len(file_paths) != len(file_names):
            print(f'DicomDataSetLoader.load() Number of file paths not equal to number of file names')
            return 
        
        filesets = {}
        for i in range(len(file_paths)):
            try:
                p = pydicom.dcmread(file_paths[i])
                if self.is_compressed(p):
                    p.decompress()
                
                if p.SeriesInstanceUID not in filesets.keys():
                    filesets[p.SeriesInstanceUID] = []
                filesets[p.SeriesInstanceUID].append((file_paths[i], p)) # Append both file path and DICOM object

            except pydicom.errors.InvalidDicomError as e:
                print(f'DicomDataSetLoader.load() Error loading DICOM file {file_paths[i]} ({e})')

        dataset = DataSetModel.objects.create(name='')

        for k in filesets.keys():
            for i in range(len(filesets[k])):
                print(f'{k}: {filesets[k][i][0]}')

