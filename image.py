import io
from PIL import Image


def compress_image(img_data, max_width, max_height, quality, encoding_type):
    image = Image.open(io.BytesIO(img_data))
    w = float(image.size[0])
    h = float(image.size[1])

    max_w = float(max_width)
    max_h = float(max_height)

    scale_w = max_w / w

    scale_h = max_h / h

    scale = min(scale_w, scale_h)

    new_w = w * scale
    new_h = h * scale

    re_image = image.resize((int(new_w), int(new_h)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()

    original_format = image.format

    if encoding_type == 'WebP':
        re_image.save(buf, format='webp', quality=quality)
    elif encoding_type == 'JPEG':
        re_image.convert('RGB').save(buf, format='jpeg', quality=quality)
    elif encoding_type == 'PNG':
        re_image.save(buf, format='PNG', quality=quality)
    elif encoding_type == 'BMP':
        re_image.convert('RGB').save(buf, format='BMP')
    else:
        formats_without_quality = ['BMP']
        if original_format in formats_without_quality:
            re_image.save(buf, format=original_format)
        else:
            re_image.save(buf, format=original_format, quality=quality)

    return buf.getvalue()
