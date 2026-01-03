from qt.core import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QIntValidator, QIcon, \
    Qt, QHBoxLayout, QCheckBox


class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.allow_below_min = None
        self.max_width = 480
        self.max_height = 800
        self.min_width = 480
        self.min_height = 800
        self.quality = 100
        self.encoding_type = 'BMP'

        self.__encodingType = None
        self.__encodingInfoLabel = None

        self.setWindowTitle("Bulk Image Resizer")

        layout = QVBoxLayout()
        self._info_section(layout)
        self._resolution_section(layout)
        self._quality_section(layout)
        self._conversion_section(layout)
        self._btn_section(layout)
        self.setLayout(layout)

    def _info_section(self, layout):
        info_label = QLabel("<b>Attention!</b>")
        info_label2 = QLabel("There are height compression options! Try the default ones before proceeding.")
        info_label.setTextFormat(Qt.RichText)
        info_label.setAlignment(Qt.AlignCenter)
        info_label2.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        layout.addWidget(info_label2)
        layout.addSpacing(10)
        layout.addStretch(1)

    def _resolution_section(self, layout):
        label1 = QLabel('Please indicate the maximum **width** for images:')
        self.input1 = QLineEdit()
        self.input1.setValidator(QIntValidator(10, 5000))
        self.input1.setText(str(self.max_width))
        layout.addWidget(label1)
        layout.addWidget(self.input1)

        label_h = QLabel('Please indicate the maximum **height** for images:')
        self.input_h = QLineEdit()
        self.input_h.setValidator(QIntValidator(10, 5000))
        self.input_h.setText(str(self.max_height))
        layout.addWidget(label_h)
        layout.addWidget(self.input_h)

        label_min_w = QLabel('Please indicate the minimum **width** for images:')
        self.input_min_w = QLineEdit()
        self.input_min_w.setValidator(QIntValidator(10, 5000))
        self.input_min_w.setText(str(self.min_width))
        layout.addWidget(label_min_w)
        layout.addWidget(self.input_min_w)

        label_min_h = QLabel('Please indicate the minimum **height** for images:')
        self.input_min_h = QLineEdit()
        self.input_min_h.setValidator(QIntValidator(10, 5000))
        self.input_min_h.setText(str(self.min_height))
        layout.addWidget(label_min_h)
        layout.addWidget(self.input_min_h)

        self.allow_below_min_checkbox = QCheckBox("Allow images below minimum dimensions to be converted without resizing")
        self.allow_below_min_checkbox.setChecked(True)
        layout.addWidget(self.allow_below_min_checkbox)

    def _quality_section(self, layout):
        label2 = QLabel('Please indicate the quality for webp codec conversion (it is ok to keep it at 100%):')
        self.input2 = QLineEdit()
        self.input2.setValidator(QIntValidator(50, 100))
        self.input2.setText(str(self.quality))
        layout.addWidget(label2)
        layout.addWidget(self.input2)

    def _conversion_section(self, layout):
        h_box_label = QHBoxLayout()
        tooltip_label = QLabel()
        icon = QIcon.ic('dialog_information.png')
        tooltip_label.setPixmap(icon.pixmap(16, 16))
        tooltip_label.setToolTip('PNG: compression is applied by reducing bitrate of colors\n'
                                 'JPEG: compression is based on human visual perception\n'
                                 'WebP: compression is based on predictive & entropy coding\n'
                                 'BMP: compression is ignored')
        h_box_label.addWidget(QLabel("Pick encoding type:"))
        h_box_label.addWidget(tooltip_label)
        h_box_label.setAlignment(Qt.AlignLeft)

        self.__encodingType = QComboBox(self)
        self.__encodingType.addItem('BMP')
        self.__encodingType.addItem('PNG')
        self.__encodingType.addItem('JPEG')
        self.__encodingType.addItem('WebP')
        self.__encodingType.addItem('Keep current')
        self.__encodingType.currentIndexChanged.connect(self.type_changed)
        self.__encodingInfoLabel = QLabel(self)
        self.__encodingInfoLabel.setStyleSheet('border: 2px solid red; padding: 8px;')
        self.__encodingInfoLabel.setText('<b>ATTENTION!</b> Currently there is <b>NO</b> handheld device that '
                                       'correctly support WebP format!')
        self.__encodingInfoLabel.setAlignment(Qt.AlignCenter)
        self.__encodingInfoLabel.setTextFormat(Qt.RichText)
        self.__encodingInfoLabel.hide()

        layout.addLayout(h_box_label)
        layout.addWidget(self.__encodingType)
        layout.addWidget(self.__encodingInfoLabel)

    def _btn_section(self, layout):
        button_layout = QHBoxLayout()
        submit_button = QPushButton('OK')
        submit_button.clicked.connect(self.submit)
        button_layout.addWidget(submit_button)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def type_changed(self):
        selected_option = self.__encodingType.currentText()
        if selected_option == 'WebP':
            self.__encodingInfoLabel.show()
        else:
            self.__encodingInfoLabel.hide()

    def submit(self):
        self.max_width = int(self.input1.text())
        self.max_height = int(self.input_h.text())
        self.min_width = int(self.input_min_w.text())
        self.min_height = int(self.input_min_h.text())
        self.quality = int(self.input2.text())
        self.encoding_type = self.__encodingType.currentText()
        self.allow_below_min = self.allow_below_min_checkbox.isChecked()
        self.accept()
