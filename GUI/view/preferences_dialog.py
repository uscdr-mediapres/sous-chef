from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QInputDialog, QSlider, QDialogButtonBox, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal


class PreferencesDialog(QDialog):
    change_policy_clicked = pyqtSignal(str, str)
    edit_license_clicked = pyqtSignal(str, bool)
    cpu_cores_changed = pyqtSignal(int)

    def __init__(self, dpx_policy=None, mkv_policy=None, max_cores=0, selected_cores=0, license_version=None):
        super().__init__()

        self.dpx_policy = str(dpx_policy) if dpx_policy else ""
        self.mkv_policy = str(mkv_policy) if mkv_policy else ""
        self.license_version = str(license_version) if license_version else None

        self.max_cores = max_cores
        self.selected_cores = selected_cores

        self.setWindowTitle("Configuration Settings")
        self.setFixedSize(650, 500)

        # Layout
        layout = QVBoxLayout()

        # DPX Policy Section
        dpx_frame = QFrame()
        dpx_frame.setFrameShape(QFrame.StyledPanel)
        dpx_layout = QVBoxLayout()

        dpx_header = QLabel("DPX Policy File")
        dpx_header.setStyleSheet("font-weight: bold; font-size: 16px;")
        dpx_layout.addWidget(dpx_header)

        dpx_policy_layout = QHBoxLayout()

        self.dpx_policy_label = QLabel(self.dpx_policy or "No file selected")
        dpx_policy_layout.addWidget(self.dpx_policy_label)

        dpx_button = QPushButton("Select Default DPX Policy")
        dpx_button.clicked.connect(self.on_select_dpx_policy)
        dpx_policy_layout.addWidget(dpx_button)

        dpx_layout.addLayout(dpx_policy_layout)
        dpx_frame.setLayout(dpx_layout)
        layout.addWidget(dpx_frame)

        # MKV Policy Section
        mkv_frame = QFrame()
        mkv_frame.setFrameShape(QFrame.StyledPanel)
        mkv_layout = QVBoxLayout()

        mkv_header = QLabel("MKV Policy File")
        mkv_header.setStyleSheet("font-weight: bold; font-size: 16px;")
        mkv_layout.addWidget(mkv_header)

        mkv_policy_layout = QHBoxLayout()

        self.mkv_policy_label = QLabel(self.mkv_policy or "No file selected")
        mkv_policy_layout.addWidget(self.mkv_policy_label)

        mkv_button = QPushButton("Select Default MKV Policy")
        mkv_button.clicked.connect(self.on_select_mkv_policy)
        mkv_policy_layout.addWidget(mkv_button)

        mkv_layout.addLayout(mkv_policy_layout)
        mkv_frame.setLayout(mkv_layout)
        layout.addWidget(mkv_frame)

        # License Section
        license_frame = QFrame()
        license_frame.setFrameShape(QFrame.StyledPanel)
        license_layout = QVBoxLayout()

        license_header = QLabel("License Settings")
        license_header.setStyleSheet("font-weight: bold; font-size: 16px;")
        license_layout.addWidget(license_header)

        license_version_layout = QHBoxLayout()

        self.license_label = QLabel(self.license_version or "No license version set")
        license_version_layout.addWidget(self.license_label)

        edit_button = QPushButton("Edit License")
        edit_button.clicked.connect(self.on_edit_license_clicked)
        license_version_layout.addWidget(edit_button)

        license_layout.addLayout(license_version_layout)
        license_frame.setLayout(license_layout)
        layout.addWidget(license_frame)

        # CPU Affinity Section
        cpu_cores_frame = QFrame()
        cpu_cores_frame.setFrameShape(QFrame.StyledPanel)
        cpu_cores_layout = QVBoxLayout()

        cpu_cores_header = QLabel("CPU Cores Settings")
        cpu_cores_header.setStyleSheet("font-weight: bold; font-size: 16px;")
        cpu_cores_layout.addWidget(cpu_cores_header)

        cpu_cores_settings_layout = QHBoxLayout()

        self.cpu_cores_label = QLabel(f"Number of Cores: {self.selected_cores}")
        cpu_cores_settings_layout.addWidget(self.cpu_cores_label)

        self.cpu_cores_slider = QSlider(Qt.Horizontal)
        self.cpu_cores_slider.setMinimum(1)
        self.cpu_cores_slider.setMaximum(self.max_cores)
        self.cpu_cores_slider.setValue(self.selected_cores)
        self.cpu_cores_slider.valueChanged.connect(self.on_cpu_cores_slider_changed)
        cpu_cores_settings_layout.addWidget(self.cpu_cores_slider)

        cpu_cores_layout.addLayout(cpu_cores_settings_layout)
        cpu_cores_frame.setLayout(cpu_cores_layout)
        layout.addWidget(cpu_cores_frame)

        # Dialog Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def on_select_dpx_policy(self):
        """Open a file dialog to select a DPX policy file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Default DPX Policy File", "", "XML Files ("
                                                                                               "*.xml);;All Files (*)")
        if file_path:
            self.dpx_policy = file_path
            self.dpx_policy_label.setText(file_path)
            self.change_policy_clicked.emit("DPX_POLICY", self.dpx_policy)

    def on_select_mkv_policy(self):
        """Open a file dialog to select an MKV policy file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Default MKV Policy File", "", "XML Files ("
                                                                                               "*.xml);;All Files (*)")
        if file_path:
            self.mkv_policy = file_path
            self.mkv_policy_label.setText(file_path)
            self.change_policy_clicked.emit("MKV_POLICY", self.mkv_policy)

    def on_edit_license_clicked(self):
        """Prompt user for a new license version and update the display."""
        new_license, ok = QInputDialog.getText(self, "Add License", "Enter new license version (optional):")
        if ok:
            self.license_version = new_license.strip() or None
            self.license_label.setText(self.license_version or "No license version set")
            self.edit_license_clicked.emit(new_license, ok)

    def on_cpu_cores_slider_changed(self, value):
        """Handle changes to the CPU cores slider."""
        self.selected_cores = value
        self.cpu_cores_label.setText(f"Number of Cores: {value}")
        self.cpu_cores_changed.emit(value)  # Emit signal with the new core count

    def update_license_display(self, license_version):
        """Update the license display."""
        if license_version:
            self.license_label.setText(f"Current License: {license_version}")
        else:
            self.license_label.setText("No license version set.")

    def get_config_data(self):
        """Return the current configuration."""
        return {
            "DPX_POLICY": self.dpx_policy,
            "MKV_POLICY": self.mkv_policy,
            "RAWCOOKED_LICENSE_VERSION": self.license_version,
            "CPU_CORES": self.selected_cores,
        }
