import shutil
from pathlib import Path
from uuid import uuid4

import requests
from PIL import Image, ImageDraw, ImageFont
from pybites_tools.aws import upload_to_s3

TEXT_COLOR = (0, 0, 0, 255)  # black, 100% opacity
TMP = Path("/tmp")
# = Mac, look at your local OS fonts or adjust code to download a font.ttf
DEFAULT_FONT = "NewYork.ttf"


def _download_file(url, destination=TMP, fname="image.jpg"):
    tempfile = destination / fname

    resp = requests.get(url, stream=True)
    if resp.status_code == 200:
        with open(tempfile, "wb") as f:
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, f)

    return tempfile


def _add_text(
    image,
    base,
    text,
    height_offset,
    *,
    font_size=100,
    fill=TEXT_COLOR
):
    """Adds text on the image canvas"""
    font = ImageFont.truetype(font=DEFAULT_FONT, size=font_size)
    draw_context = ImageDraw.Draw(image)
    width, _ = draw_context.textbbox((0, 0), text, font=font)[2:4]
    # align name horizontally - https://stackoverflow.com/a/1970930
    offset = ((base.size[0] - width) / 2, height_offset)
    draw_context.text(offset, text, font=font, fill=fill)


def create_certificate(
    template,
    name,
    *,
    name_vertical_offset=550,
):
    """
    Creates certificate with name using template png url.
    Offsets depend on certificate = trial and error.
    """
    template = _download_file(template)

    name = name.title()
    name_cleaned = name.strip().replace(" ", "_").lower()

    out_file = TMP / f"{name_cleaned}_{uuid4()}.png"

    base = Image.open(template).convert("RGBA")
    image = Image.new("RGBA", base.size)

    _add_text(image, base, name, name_vertical_offset)

    out = Image.alpha_composite(base, image)
    out.save(out_file)

    s3_url = upload_to_s3(out_file)
    Path(out_file).unlink()

    return s3_url


if __name__ == "__main__":
    template = "https://t.ly/EauI"
    create_certificate(template, "Simão Araújo")
