import pydicom
import numpy as np


def main():
    p = pydicom.dcmread('D:\\Mosamatic\\Web 3.0\\L3CT\\130066.dcm.472x472')
    pixel_array = p.pixel_array
    hu_array = pixel_array * p.RescaleSlope + p.RescaleIntercept
    hu_air = -1000
    padded_hu_array = np.full((512, 512), hu_air, dtype=hu_array.dtype)
    padded_hu_array[:pixel_array.shape[0], :pixel_array.shape[1]] = hu_array
    pixel_array_padded = (padded_hu_array - p.RescaleIntercept) / p.RescaleSlope
    pixel_array_padded = pixel_array_padded.astype(pixel_array.dtype)
    p.PixelData = pixel_array_padded.tobytes()
    p.Rows = 512
    p.Columns = 512
    p.save_as('D:\\Mosamatic\\Web 3.0\\padded.dcm')



if __name__ == '__main__':
    main()