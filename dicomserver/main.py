import os
import tempfile

from pynetdicom import AE, evt
from pynetdicom.sop_class import CTImageStorage, MRImageStorage

DICOMSTORAGE = '/data/dicomstorage' if os.getenv('DOCKER', None) == 'true' else os.path.join(tempfile.gettempdir(), 'mosamatic/data/dicomstorage')
os.makedirs(DICOMSTORAGE, exist_ok=True)
PORT = int(os.getenv('PORT', '104'))

storage_sop_classes = [CTImageStorage, MRImageStorage]


def handle_store(event, storage_dir=DICOMSTORAGE):
    ds = event.dataset
    ds.file_meta = event.file_meta
    filename = f'{storage_dir}/{ds.SOPInstanceUID}.dcm'
    ds.save_as(filename)
    return 0x0000  # Success

ae = AE(ae_title='MOSW3')

for sop_class in storage_sop_classes:
    ae.add_supported_context(sop_class)

handlers = [(evt.EVT_C_STORE, handle_store)]

print(f'Starting Mosamatic Web 3.0 DICOM server on port {PORT}...')
ae.start_server(('', PORT), block=True, evt_handlers=handlers)