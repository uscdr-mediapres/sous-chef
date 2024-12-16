from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, QToolBar, QAction, QVBoxLayout, QLabel, QDesktopWidget, QWidget, QStatusBar, QPushButton,
    QHBoxLayout, QSplitter, QFrame, QSizePolicy, QFileDialog, QSpacerItem,
    QMessageBox, QScrollArea
)
from GUI.view.folder_table_view import FolderTableWidget


def create_frame(label):
    frame = QFrame()
    frame.setFrameStyle(QFrame.StyledPanel)
    frame_label = QLabel(label)
    frame_label.setAlignment(Qt.AlignCenter)
    frame_layout = QVBoxLayout()
    frame_layout.addWidget(frame_label)
    frame.setLayout(frame_layout)
    return frame


def change_button_size_policy(button):
    button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    button.adjustSize()
    return button


def create_button_layout(*buttons, alignment=None):
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)

    for button in buttons:
        layout.addWidget(button)

    if alignment:
        layout.setAlignment(alignment)

    return layout


class View(QMainWindow):
    folder_policy_details = pyqtSignal()

    def __init__(self, project_root):
        super().__init__()
        self.project_root = project_root

        self.load_styles()
        self.setWindowTitle("RawCooked USC DR")
        self.resize(500, 350)
        self.center()

        self.about_action = QAction()
        self.pref_action = QAction()
        self.init_statusbar()
        self.init_about_action()
        self.init_pref_action()
        self.init_toolbar()

        self.folder_button = QPushButton("Select Folders to Cook")
        self.output_button = QPushButton("Select Output Folder")
        self.output_folder = ""
        self.output_folder_label = QLabel()
        self.empty_output_folder_text = "Output Folder: (none selected)"
        self.output_folder_label.setText(self.empty_output_folder_text)

        self.run_button = QPushButton("Run")

        self.buttons_widget = None

        self.folder_table = FolderTableWidget(self)

        self.log_container = QWidget()
        self.log_layout = QVBoxLayout(self.log_container)

        self.progress_container = QWidget()
        self.progress_layout = QVBoxLayout(self.progress_container)

        self.splitter = None

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.init_buttons_widget()
        layout.addWidget(self.buttons_widget)
        self.init_splitter()
        layout.addWidget(self.splitter)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.add_connections()

        self.showMaximized()

    def load_styles(self):
        style_sheet_path = self.project_root / "GUI" / "styles" / "styles.qss"
        with open(style_sheet_path, "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_statusbar(self):
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

    def init_about_action(self):
        self.about_action = QAction("About", self)
        self.about_action.setStatusTip("About")

    def init_pref_action(self):
        self.pref_action = QAction("Preferences", self)
        self.pref_action.setStatusTip("Preferences")

    def init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.addAction(self.pref_action)
        toolbar.addAction(self.about_action)
        self.addToolBar(toolbar)

    def init_buttons_widget(self):
        change_button_size_policy(self.folder_button)
        change_button_size_policy(self.output_button)
        change_button_size_policy(self.output_folder_label)
        change_button_size_policy(self.run_button)

        left_layout = create_button_layout(self.folder_button, alignment=Qt.AlignLeft)

        right_layout = create_button_layout(self.output_button, self.output_folder_label, alignment=Qt.AlignRight)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        right_layout.addItem(spacer)
        right_layout.addWidget(self.run_button)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addLayout(left_layout)
        button_layout.addLayout(right_layout)

        self.buttons_widget = QWidget()
        self.buttons_widget.setLayout(button_layout)
        self.buttons_widget.setFixedHeight(20)

    def init_splitter(self):
        left_top_frame = self.folder_table
        left_bottom_frame = self.progress_container

        # Make left bottom frame scrollable
        left_bottom_scroll_area = QScrollArea()
        left_bottom_scroll_area.setWidgetResizable(True)
        left_bottom_scroll_area.setWidget(left_bottom_frame)

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(left_top_frame)
        left_splitter.addWidget(left_bottom_scroll_area)
        left_splitter.setSizes([150, 120])

        # right_frame = self.log_container
        right_frame_scroll_area = QScrollArea()
        right_frame_scroll_area.setWidgetResizable(True)
        self.log_container.setMinimumWidth(150)
        right_frame_scroll_area.setWidget(self.log_container)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(left_splitter)
        self.splitter.addWidget(right_frame_scroll_area)
        self.splitter.addWidget(self.buttons_widget)
        self.splitter.setSizes([350, 150, 20])

        self.buttons_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Add stretch factors if necessary
        self.splitter.setStretchFactor(0, 1)  # Allow left splitter to stretch
        self.splitter.setStretchFactor(1, 1)  # Allow right frame (logs) to stretch
        self.splitter.setStretchFactor(2, 0)  # Fix the size of the buttons widget

    def select_folders(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Cook")
        if folder:
            self.folder_policy_details.emit()
            self.folder_table.add_folder_to_table(folder)

    def select_output_folder(self):
        self.output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if self.output_folder:
            self.output_folder_label.setText("Output Folder: " + self.output_folder)

    def add_connections(self):
        self.folder_button.clicked.connect(self.select_folders)
        self.output_button.clicked.connect(self.select_output_folder)

    def get_row_count(self):
        if self.folder_table.rowCount() == 0:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("No Folders Selected")
            msg_box.setText("Please select folders containing DPX Sequences to process")
            msg_box.exec_()
        return self.folder_table.rowCount()

    def get_output_folder(self):
        if self.output_folder_label.text() == self.empty_output_folder_text:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Output Folder Not Set")
            msg_box.setText("Please select an output folder for the processed videos to be stored")
            msg_box.exec_()
            return ""
        return self.output_folder
