import io
from PIL import Image


def compress_image(img_data, max_width, max_height, quality, encoding_type, skip_resize=False):
        image = Image.open(io.BytesIO(img_data))

        if not skip_resize:
            w = float(image.size[0])
            h = float(image.size[1])

            max_w = float(max_width)
            max_h = float(max_height)

            scale_w = max_w / w
            scale_h = max_h / h

            scale = min(scale_w, scale_h)

            new_w = w * scale
            new_h = h * scale

            image = image.resize((int(new_w), int(new_h)), Image.Resampling.LANCZOS)

        buf = io.BytesIO()
        original_format = image.format

        if encoding_type == 'WebP':
            image.save(buf, format='webp', quality=quality)
        elif encoding_type == 'JPEG':
            image.convert('RGB').save(buf, format='jpeg', quality=quality)
        elif encoding_type == 'PNG':
            image.save(buf, format='PNG', quality=quality)
        elif encoding_type == 'BMP':
            image.convert('RGB').save(buf, format='BMP')
        else:
            formats_without_quality = ['BMP']
            if original_format in formats_without_quality:
                image.save(buf, format=original_format)
            else:
                image.save(buf, format=original_format, quality=quality)

        return buf.getvalue()
