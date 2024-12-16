import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QTextEdit


class ProgressBarView(QWidget):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

        self.progress_bar_label = QLabel(os.path.basename(self.filename) + " progress:")
        self.progress_bar_label.setToolTip(filename)

        layout = QVBoxLayout()

        # Label for section
        self.section_label = QLabel("--- Starting DPX Assessment ---")
        self.section_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar_label)
        layout.addWidget(self.section_label)

        # Progress bar with custom style
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Frame Number: %p%")

        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def set_section_text(self, text):
        """Updates the section label text."""
        self.section_label.setText(text)

    def update_progress_bar(self, progress_name, value):
        """Updates the progress bar format and value."""
        if "Error" in progress_name:
            self.progress_bar.setProperty("class", "error")
            self.style().polish(self.progress_bar)
            self.progress_bar.setFormat(f"{progress_name}")
        else:
            self.progress_bar.setFormat(f"{progress_name}: %p%")
        self.progress_bar.setValue(int(value))
