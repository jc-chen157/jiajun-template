from domino.testing import piece_dry_run
from pathlib import Path
from PIL import Image
from io import BytesIO
import base64


# Reuse the test image from ImageFilterPiece
img_path = str(Path(__file__).parent / "../ImageFilterPiece/test_image.png")
img = Image.open(img_path)
buffered = BytesIO()
img.save(buffered, format="PNG")
image_bytes = buffered.getvalue()
base64_image = base64.b64encode(image_bytes).decode("utf-8")


def test_bulkimagefilterpiece_multiple_images():
    input_data = dict(
        input_images=[base64_image, base64_image],
        sepia=True,
        blue=True,
        output_type="both"
    )
    piece_output = piece_dry_run(
        piece_name="BulkImageFilterPiece",
        input_data=input_data
    )
    assert piece_output is not None
    assert len(piece_output['image_base64_strings']) == 2
    assert len(piece_output['image_file_paths']) == 2
    assert all(p.endswith('.png') for p in piece_output['image_file_paths'])
    assert all(s != "" for s in piece_output['image_base64_strings'])


def test_bulkimagefilterpiece_empty_list():
    input_data = dict(
        input_images=[],
        sepia=True,
        output_type="base64_string"
    )
    piece_output = piece_dry_run(
        piece_name="BulkImageFilterPiece",
        input_data=input_data
    )
    assert piece_output['image_base64_strings'] == []
    assert piece_output['image_file_paths'] == []


def test_bulkimagefilterpiece_base64_only():
    input_data = dict(
        input_images=[base64_image],
        warm=True,
        output_type="base64_string"
    )
    piece_output = piece_dry_run(
        piece_name="BulkImageFilterPiece",
        input_data=input_data
    )
    assert len(piece_output['image_base64_strings']) == 1
    assert piece_output['image_base64_strings'][0] != ""
    assert piece_output['image_file_paths'][0] == ""
