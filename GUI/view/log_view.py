import os.path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel
from PyQt5.QtGui import QTextCursor


class LogWidget(QWidget):
    def __init__(self, filename, parent=None):
        super().__init__(parent)
        # Text edit to display log contents
        self.filename = filename
        self.log_label = QLabel("Info Log: " + os.path.basename(self.filename))
        self.log_label.setToolTip(filename)
        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.log_label)
        layout.addWidget(self.log_display)
        self.setLayout(layout)

    def append_log_content(self, content):
        """Appends the log content to the text area."""
        self.log_display.moveCursor(QTextCursor.End)  # Move to the end before appending
        self.log_display.insertPlainText(content)
        self.log_display.ensureCursorVisible()  # Ensure the new content is visible


