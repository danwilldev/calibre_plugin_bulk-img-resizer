#!/usr/bin/env python
# vim:fileencoding=utf-8

__license__ = 'MIT'
__copyright__ = '2024, Artur Kupiec'

import os
import io
from PIL import Image
from calibre.gui2 import error_dialog, warning_dialog
from calibre.gui2.tweak_book import current_container
from calibre.gui2.tweak_book.plugin import Tool
from calibre.ebooks.oeb.base import JPEG_MIME, PNG_MIME, WEBP_MIME, GIF_MIME
from calibre.ebooks.oeb.polish.replace import rename_files
from qt.core import QAction, QInputDialog, QProgressDialog, Qt, QTimer, QMessageBox
from calibre_plugins.bulk_img_resizer.ui import ConfigDialog
from calibre_plugins.bulk_img_resizer.image import compress_image
from calibre.utils.localization import _

def replace_extension(file_name, new_extension):
    base_name, _ = os.path.splitext(file_name)
    return base_name + new_extension


class BulkImgReducer(Tool):
    name = 'bulk-img-resizer'
    allowed_in_toolbar = True
    allowed_in_menu = True
    default_shortcut = ('Ctrl+Shift+Alt+R',)

    RASTER_IMAGES = {JPEG_MIME, PNG_MIME, WEBP_MIME, GIF_MIME}

    def __init__(self):
        self.config = None
        self.job_data = None
        self.pd_timer = QTimer()

    def create_action(self, for_toolbar=True):
        ac = QAction(get_icons('images/icon.png'), 'Bulk Image Resizer', self.gui)  # noqa
        if not for_toolbar:
            self.register_shortcut(ac, self.name, default_keys=self.default_shortcut)
        ac.triggered.connect(self.ask_user)
        return ac

    def ask_user(self):
        if not self.ensure_book(_('You must first open a book in order to compress images.')):
            return

        dialog = ConfigDialog()

        if dialog.exec_() != ConfigDialog.Accepted:
            return

        self.config = (
            dialog.max_width,
            dialog.max_height,
            dialog.quality,
            dialog.encoding_type,
            dialog.min_width,
            dialog.min_height,
            dialog.allow_below_min
        )
        print('CONFIG', self.config)

        self.boss.commit_all_editors_to_container()
        self.boss.add_savepoint('Before: Resizing images')
        self.mimify_images()

    def mimify_images(self):
        container = self.current_container
        images = self.get_images_from_collection(container)

        if len(images) == 0:
            dialog = QMessageBox()
            dialog.setText('No images found!')
            return

        # Unpack config for easier access
        max_w, max_h, quality, enc, min_w, min_h, allow_below = self.config

        # Determine target boundaries for orientation-independent check
        target_short = min(min_w, min_h)
        target_long = max(min_w, min_h)

        filtered_images = []

        for img in images:
            try:
                img_data = container.parsed(img)
                with Image.open(io.BytesIO(img_data)) as image:
                    iw, ih = image.size

                    is_large_enough = (iw > max_w or ih > max_h)

                    if is_large_enough:
                        filtered_images.append((img, True))  # Resize and convert
                    elif allow_below:
                        filtered_images.append((img, False))  # Only convert
            except Exception:
                continue

        if len(filtered_images) == 0:
            QMessageBox.information(self.gui, 'Finished', 'No images meet the size requirements.')
            return

        progress = self.create_progres_dialog(len(filtered_images))
        self.job_data = (filtered_images, filtered_images.copy(), progress, container)

        self.pd_timer.timeout.connect(self.do_one)
        self.pd_timer.start()

    def do_one(self):
        filtered_images, all_images, progress, container = self.job_data
        max_width, max_height, quality, encoding_type, min_w, min_h, allow_below = self.config

        if len(filtered_images) == 0 or progress.wasCanceled():
            self.pd_timer.stop()
            self.do_end()
            return

        name, resize = filtered_images.pop()
        try:
            img_data = container.parsed(name)
            if resize:
                new_image = compress_image(img_data, max_width, max_height, quality, encoding_type)
            else:
                new_image = compress_image(img_data, max_width, max_height, quality, encoding_type, skip_resize=True)
            container.replace(name, new_image)
        except Exception:
            import traceback
            warning_dialog(self.gui,
                           _('Image Resize Failed'),
                           _(f'The image "{name}" could not be resized. It may be corrupted or in an unsupported format.'),
                           det_msg=traceback.format_exc(), show=True)

        index = len(all_images) - len(filtered_images)
        progress.setValue(index)

    def do_end(self):
        _, _, _, encoding_type, _, _, _ = self.config
        _, all_images, progress, container = self.job_data

        progress.setWindowTitle('Renaming files...')
        replace_map = {}

        for item in all_images:
            name = item[0]  # Get the actual filename from the tuple

            if encoding_type == 'WebP':
                value = replace_extension(name, '.webp')
            elif encoding_type == 'JPEG':
                value = replace_extension(name, '.jpg')
            elif encoding_type == 'PNG':
                value = replace_extension(name, '.png')
            elif encoding_type == 'BMP':
                value = replace_extension(name, '.bmp')
            else:
                break

            if name != value:
                replace_map[name] = value

        rename_files(container, replace_map)

        progress.setValue(len(all_images) + 1)

        self.boss.show_current_diff()
        self.boss.apply_container_update_to_gui()

    def ensure_book(self, msg=None):
        msg = msg or _('No book is currently open. You must first open a book.')
        if current_container() is None:
            error_dialog(self.gui, _('No book open'), msg, show=True)
            return False
        return True

    def get_images_from_collection(self, container):
        images = []
        for name, media_type in container.mime_map.items():
            if media_type in self.RASTER_IMAGES:
                images.append(name)

        return images

    def create_progres_dialog(self, image_count):
        progress = QProgressDialog('Resizing images...', _('&Stop'), 0, image_count + 1, self.gui)
        progress.setWindowTitle('Resizing...')
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setValue(0)
        progress.show()
        return progress
