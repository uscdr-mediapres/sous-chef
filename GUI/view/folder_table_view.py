import os.path

from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QLabel, QCheckBox, QWidget, QHBoxLayout, QSizePolicy, \
    QPushButton, QFileDialog
from pathlib import Path


class FolderTableWidget(QTableWidget):

    def __init__(self, parent=None):
        super(FolderTableWidget, self).__init__(parent)
        self.default_dpx_policy = None
        self.default_mkv_policy = None

        self.setColumnCount(9)

        self.setHorizontalHeaderLabels(
            ["Folder Path", "Check Gaps", "Check DPX Policy", "DPX Policy Path", "Check MKV Policy", "MKV Policy Path",
             "Verify MD5 Checksum", "Process In-Place", ""])

        self.setShowGrid(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        for col in range(self.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

    def change_policy_file_path(self, policy_path_label):
        new_policy_file_path, _ = QFileDialog.getOpenFileName(self, "Select Policy File")
        if new_policy_file_path:
            policy_file_name = os.path.basename(new_policy_file_path)
            policy_path_label.setText(policy_file_name)
            policy_path_label.setStatusTip(new_policy_file_path)

    def toggle_label(self, state, row_position, col_position):
        next_widget = self.cellWidget(row_position, col_position + 1)
        next_label = next_widget.layout().itemAt(0).widget()
        if state == Qt.Checked:
            next_label.setEnabled(True)
        else:
            next_label.setEnabled(False)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if obj.layout() is not None:
                for i in range(obj.layout().count()):
                    widget = obj.layout().itemAt(i).widget()
                    if isinstance(widget, QCheckBox):
                        widget.toggle()
                        break
        return super().eventFilter(obj, event)

    def add_checkbox(self, row_position, col_position, checked=True, next_col_label=False):
        check_box = QCheckBox()
        check_box.setChecked(checked)
        check_box_widget = QWidget()
        check_box_layout = QHBoxLayout()
        check_box_layout.addWidget(check_box)
        check_box_layout.setAlignment(Qt.AlignCenter)
        check_box_widget.setLayout(check_box_layout)

        self.setCellWidget(row_position, col_position, check_box_widget)

        check_box_widget.installEventFilter(self)

        if next_col_label:
            check_box.stateChanged.connect(lambda state: self.toggle_label(state, row_position, col_position))

    def add_policy_path_to_table(self, row_position, col_position, policy_path):
        policy_file_name = os.path.basename(policy_path)
        if not os.path.isfile(policy_path):
            policy_file_name = "No policy selected"
        policy_label = QLabel(policy_file_name)
        policy_label.setStatusTip(policy_path)

        change_path_button = QPushButton("Change")
        change_path_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        change_path_button.setFixedSize(change_path_button.sizeHint())
        change_path_button.clicked.connect(lambda: self.change_policy_file_path(policy_label))

        policy_widget = QWidget()
        policy_layout = QHBoxLayout()
        policy_layout.addWidget(policy_label)
        policy_layout.addWidget(change_path_button)
        policy_layout.setContentsMargins(1, 1, 1, 1)

        policy_widget.setLayout(policy_layout)
        self.setCellWidget(row_position, col_position, policy_widget)

    def delete_row(self, button):
        row_position = self.indexAt(button.parent().pos()).row()
        self.removeRow(row_position)

    def delete_row_by_name(self, filepath):
        # Iterate over the rows of the table widget in reverse
        for row in reversed(range(self.rowCount())):
            item = self.get_table_data()[row]['sequence_folder_path']
            if item == filepath:
                self.removeRow(row)

    def add_delete_button(self, row_position, col_position):
        delete_widget = QWidget()
        delete_layout = QHBoxLayout()
        delete_button = QPushButton("X")
        delete_button.setFixedSize(delete_button.sizeHint())
        delete_button.setStyleSheet("padding: 0; margin: 0;")
        delete_button.setFixedWidth(20)
        delete_layout.addWidget(delete_button)
        delete_layout.setContentsMargins(0, 0, 0, 0)
        delete_widget.setLayout(delete_layout)

        delete_button.clicked.connect(lambda: self.delete_row(delete_button))

        self.setCellWidget(row_position, col_position, delete_widget)

    def add_folder_to_table(self, folder):
        row_position = self.rowCount()  # Use self to get the row count
        self.insertRow(row_position)

        folder_name_label = QLabel()
        folder_name_label.setText(folder)
        folder_name_label.setStatusTip(folder)
        self.setCellWidget(row_position, 0, folder_name_label)
        self.add_checkbox(row_position, 1)
        self.add_checkbox(row_position, 2, True, True)
        self.add_policy_path_to_table(row_position, 3, self.default_dpx_policy)
        self.add_checkbox(row_position, 4, True, True)
        self.add_policy_path_to_table(row_position, 5, self.default_mkv_policy)
        self.add_checkbox(row_position, 6)
        self.add_checkbox(row_position, 7)
        self.add_delete_button(row_position, 8)

    def get_table_data(self):
        data = []
        config_keys = ["sequence_folder_path", "gap_check", "dpx_policy_check", "dpx_policy_path", "mkv_policy_check",
                       "mkv_policy_path", "frame_md5", "in_place"]
        for row in range(self.rowCount()):
            row_data = {}
            for col in range(self.columnCount()-1):  # Ignoring the last column because it is the delete button
                cell_widget = self.cellWidget(row, col)
                key = config_keys[col]
                if cell_widget:
                    if isinstance(cell_widget, QLabel):
                        row_data[key] = cell_widget.text()
                    elif isinstance(cell_widget, QWidget):
                        for child in cell_widget.children():
                            if isinstance(child, QLabel):
                                row_data[key] = child.statusTip()
                            elif isinstance(child, QCheckBox):
                                row_data[key] = child.isChecked()
                    else:
                        row_data[key] = None
                else:
                    row_data[key] = None
            data.append(row_data)
        return data
