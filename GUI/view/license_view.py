from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel


class AboutWindow(QDialog):
    def __init__(self, label_text):
        super().__init__()
        self.setWindowTitle("About")

        layout = QVBoxLayout()

        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.label)

        self.setLayout(layout)
        self.adjustSize()

    def set_license(self, license_info):
        self.label.setText(license_info)
        self.adjustSize()

