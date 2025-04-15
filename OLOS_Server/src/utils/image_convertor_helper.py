import base64
import os
from PIL import Image
import numpy as np
from autotrace import Bitmap, VectorFormat
from core.constants import CoreConstants as constants


def convert_images_from_png_to_svg(images_paths):
    svg_images_paths = []
    for img_path in images_paths:
        with Image.open(img_path) as img:
            filename = os.path.splitext(img_path)[0].lower()
            # Create a bitmap.
            bitmap = Bitmap(np.asarray(img.convert("RGB")))

            # Trace the bitmap.
            vector = bitmap.trace(despeckle_level=20,
                                  despeckle_tightness=2, error_threshold=0.1, filter_iterations=0, remove_adjacent_corners=True, tangent_surround=0, noise_removal=1, color_count=16)

            # Get an SVG as a byte string.
            with open(filename + '.svg', mode='wb') as img:
                img.write(vector.encode(VectorFormat.SVG))
                svg_images_paths.append(img.name)

    return svg_images_paths


def convert_images_to_base64(images_paths):
    images_base64 = []

    for img_path in images_paths:
        # Determine the file extension
        file_extension = os.path.splitext(img_path)[1].lower()

        # Get the MIME type based on the file extension
        mime_type = constants.ACCEPTED_IMAGE_FILES_EXTENSIONS.get(
            file_extension)
        if not mime_type:
            raise ValueError(f"Unsupported file extension: {file_extension}")

        # Construct the data URL prefix
        data_url_prefix = f"data:{mime_type};base64,"

        # Read file as binary and encode to Base64
        with open(img_path, "rb") as file:
            file_content = file.read()
        base64_content = base64.b64encode(file_content).decode("utf-8")
        images_base64.append(data_url_prefix + base64_content)

    return images_base64


def convert_base64_to_image(base64_string):
    # Check if the Base64 string has a header
    decoded_data = None
    if base64_string and "," in base64_string:
        _, base64_data = base64_string.split(",", 1)

        # Decode the Base64 string
        decoded_data = base64.b64decode(base64_data)

    return decoded_data
