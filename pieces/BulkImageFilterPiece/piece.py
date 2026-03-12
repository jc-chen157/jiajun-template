from domino.base_piece import BasePiece
from .models import InputModel, OutputModel
from pathlib import Path
from PIL import Image
from io import BytesIO
import numpy as np
import base64
import os


filter_masks = {
    'sepia': ((0.393, 0.769, 0.189), (0.349, 0.686, 0.168), (0.272, 0.534, 0.131)),
    'black_and_white': ((0.333, 0.333, 0.333), (0.333, 0.333, 0.333), (0.333, 0.333, 0.333)),
    'brightness': ((1.4, 0, 0), (0, 1.4, 0), (0, 0, 1.4)),
    'darkness': ((0.6, 0, 0), (0, 0.6, 0), (0, 0, 0.6)),
    'contrast': ((1.2, 0.6, 0.6), (0.6, 1.2, 0.6), (0.6, 0.6, 1.2)),
    'red': ((1.6, 0, 0), (0, 1, 0), (0, 0, 1)),
    'green': ((1, 0, 0), (0, 1.6, 0), (0, 0, 1)),
    'blue': ((1, 0, 0), (0, 1, 0), (0, 0, 1.6)),
    'cool': ((0.9, 0, 0), (0, 1.1, 0), (0, 0, 1.3)),
    'warm': ((1.2, 0, 0), (0, 0.9, 0), (0, 0, 0.8)),
}


class BulkImageFilterPiece(BasePiece):

    def _open_image(self, input_image: str) -> Image.Image:
        """Open an image from a file path or base64 string."""
        max_path_size = int(os.pathconf('/', 'PC_PATH_MAX'))
        if len(input_image) < max_path_size and Path(input_image).exists() and Path(input_image).is_file():
            return Image.open(input_image)
        else:
            self.logger.info("Input image is not a file path, trying to decode as base64 string")
            self.logger.info(f"Base64 string length: {len(input_image)}, first 100 chars: {input_image[:100]}")
            try:
                decoded_data = base64.b64decode(input_image)
                self.logger.info(f"Decoded data size: {len(decoded_data)} bytes, first 20 bytes: {decoded_data[:20]}")
                image_stream = BytesIO(decoded_data)
                image = Image.open(image_stream)
                image.verify()
                image_stream.seek(0)
                image = Image.open(image_stream)
                self.logger.info(f"Opened image: mode={image.mode}, size={image.size}, format={image.format}")
                return image
            except Exception:
                raise ValueError("Input image is not a file path or a base64 encoded string")

    def _apply_filters(self, image: Image.Image, all_filters: list) -> Image.Image:
        """Apply filter masks to an image via numpy matrix multiplication."""
        # Convert to RGB to ensure 3 channels (handles grayscale, palette, RGBA, etc.)
        if image.mode != 'RGB':
            self.logger.info(f"Converting image from mode '{image.mode}' to 'RGB'")
            image = image.convert('RGB')
        np_image = np.array(image, dtype=float)
        self.logger.info(f"Image array shape: {np_image.shape}, dtype: {np_image.dtype}")
        for filter_name in all_filters:
            np_mask = np.array(filter_masks[filter_name], dtype=float)
            for y in range(np_image.shape[0]):
                for x in range(np_image.shape[1]):
                    rgb = np_image[y, x, :3]
                    new_rgb = np.dot(np_mask, rgb)
                    np_image[y, x, :3] = new_rgb
            np_image = np.clip(np_image, 0, 255)
        np_image = np_image.astype(np.uint8)
        return Image.fromarray(np_image)

    def piece_function(self, input_data: InputModel):
        # Collect selected filters
        all_filters = []
        for filter_name in filter_masks.keys():
            if getattr(input_data, filter_name, False):
                all_filters.append(filter_name)

        self.logger.info(f"Processing {len(input_data.input_images)} images with filters: {', '.join(all_filters)}")

        image_base64_strings = []
        image_file_paths = []

        for i, input_image in enumerate(input_data.input_images):
            self.logger.info(f"Processing image {i+1}/{len(input_data.input_images)}")

            image = self._open_image(input_image)
            modified_image = self._apply_filters(image, all_filters)

            # Save to file
            file_path = ""
            if input_data.output_type in ("file", "both"):
                file_path = f"{self.results_path}/modified_image_{i}.png"
                modified_image.save(file_path)

            # Convert to base64 string
            b64_string = ""
            if input_data.output_type in ("base64_string", "both"):
                buffered = BytesIO()
                modified_image.save(buffered, format="PNG")
                b64_string = base64.b64encode(buffered.getvalue()).decode('utf-8')

            image_base64_strings.append(b64_string)
            image_file_paths.append(file_path)

        # Display the first image result if available
        if image_base64_strings and image_base64_strings[0]:
            self.display_result = {
                "file_type": "png",
                "base64_content": image_base64_strings[0],
                "file_path": image_file_paths[0] if image_file_paths else ""
            }

        return OutputModel(
            image_base64_strings=image_base64_strings,
            image_file_paths=image_file_paths,
        )
