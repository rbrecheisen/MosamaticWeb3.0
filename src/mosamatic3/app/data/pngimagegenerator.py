import os
import numpy as np

from ..utils import is_dicom, convert_dicom_to_numpy_array, convert_numpy_array_to_png_image, ColorMap


class PngImageGenerator:
    def __init__(self) -> None:
        pass

    def run(self, file_path: str, color_map: ColorMap=None) -> str:
        png_path = None
        output_dir_path, png_file_name = os.path.split(file_path)[0], os.path.split(file_path)[1] + '.png'
        if is_dicom(file_path):
            pixels = convert_dicom_to_numpy_array(file_path)
            png_path = convert_numpy_array_to_png_image(pixels, output_dir_path, png_file_name=png_file_name)
        elif file_path.endswith('.npy'):
            pixels = np.load(file_path)
            if len(pixels.shape) == 2:
                png_path = convert_numpy_array_to_png_image(pixels, output_dir_path, color_map=color_map, png_file_name=png_file_name)
        else:
            pass
        return png_path