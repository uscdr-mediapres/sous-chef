import os
import shutil

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, QToolBar, QAction, QVBoxLayout, QLabel, QDesktopWidget, QWidget, QStatusBar, QPushButton,
    QHBoxLayout, QSplitter, QFrame, QSizePolicy, QFileDialog, QSpacerItem,
    QMessageBox, QScrollArea
)
from GUI.view.folder_table_view import FolderTableView


def create_frame(label):
    """
    Create a styled panel frame with a centered label.

    :param label: The text for the QLabel inside the frame.
    :type label: str
    :return: A QFrame object containing the label.
    :rtype: QFrame
    """
    frame = QFrame()
    frame.setFrameStyle(QFrame.StyledPanel)
    frame_label = QLabel(label)
    frame_label.setAlignment(Qt.AlignCenter)
    frame_layout = QVBoxLayout()
    frame_layout.addWidget(frame_label)
    frame.setLayout(frame_layout)
    return frame


def change_button_size_policy(button):
    """
    Adjust the size policy and dimensions of a QPushButton.

    :param button: The QPushButton to adjust.
    :type button: QPushButton
    :return: The adjusted QPushButton.
    :rtype: QPushButton
    """
    button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    button.adjustSize()
    return button


def create_button_layout(*buttons, alignment=None):
    """
    Create a horizontal layout for buttons with optional alignment.

    :param buttons: Buttons to add to the layout.
    :type buttons: QPushButton
    :param alignment: Alignment for the layout. Defaults to None.
    :type alignment: Qt.Alignment, optional
    :return: A QHBoxLayout containing the buttons.
    :rtype: QHBoxLayout
    """
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)

    for button in buttons:
        layout.addWidget(button)

    if alignment:
        layout.setAlignment(alignment)

    return layout


class View(QMainWindow):
    """
     Main window class for the RawCooked USC DR application.

     :param project_root: The root directory of the project.
     :type project_root: str
     """

    folder_policy_details = pyqtSignal()
    """
    :signal folder_policy_details: Emitted when a folder is selected
    """

    def __init__(self, project_root):
        """
       Initializes the View.

       :param project_root: Path to the log file being monitored.
       """
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
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)

        self.buttons_widget = None

        self.folder_table = FolderTableView(self)

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
        """
        Load the QSS stylesheet for the application.
        """
        style_sheet_path = self.project_root / "GUI" / "styles" / "styles.qss"
        with open(style_sheet_path, "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())

    def center(self):
        """
        Center the main window on the screen.
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_statusbar(self):
        """
        Initialize the status bar for the main window.
        """
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

    def init_about_action(self):
        """
        Initialize the 'About' action for the toolbar.
        """
        self.about_action = QAction("About", self)
        self.about_action.setStatusTip("About")

    def init_pref_action(self):
        """
        Initialize the 'Preferences' action for the toolbar.
        """
        self.pref_action = QAction("Preferences", self)
        self.pref_action.setStatusTip("Preferences")

    def init_toolbar(self):
        """
        Initialize the main toolbar and add actions.
        """
        toolbar = QToolBar("Main Toolbar")
        toolbar.addAction(self.pref_action)
        toolbar.addAction(self.about_action)
        self.addToolBar(toolbar)

    def init_buttons_widget(self):
        """
         Initialize the buttons widget with layout and alignment.
         """
        change_button_size_policy(self.folder_button)
        change_button_size_policy(self.output_button)
        change_button_size_policy(self.output_folder_label)
        change_button_size_policy(self.run_button)

        left_layout = create_button_layout(self.folder_button, alignment=Qt.AlignLeft)

        right_layout = create_button_layout(self.output_button, self.output_folder_label, alignment=Qt.AlignRight)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        right_layout.addItem(spacer)
        right_layout.addWidget(self.run_button)
        right_layout.addWidget(self.cancel_button)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addLayout(left_layout)
        button_layout.addLayout(right_layout)

        self.buttons_widget = QWidget()
        self.buttons_widget.setLayout(button_layout)
        self.buttons_widget.setFixedHeight(20)

    def init_splitter(self):
        """
        Initialize the main splitter containing folder table, progress, and logs.
        """
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
        """
        Open a dialog to select folders and add them to the table.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Cook")
        if folder:
            self.folder_policy_details.emit()
            self.folder_table.add_folder_to_table(folder)

    def check_valid_output_folder(self, folder):
        """
        Check if the output folder is valid and handle conflicts.

        :param folder: Path to the selected output folder.
        :type folder: str
        :return: True if valid, False otherwise.
        :rtype: bool
        """
        working_dir = os.path.join(folder, "working_directory")
        if os.path.exists(working_dir):
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"'{working_dir}' already exists in the selected output folder. Do you want to delete it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                try:
                    shutil.rmtree(working_dir)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete '{working_dir}': {str(e)}")
                    return False
            else:
                return False  # User chose not to delete, so folder is not usable
        return True

    def select_output_folder(self):
        """
        Open a dialog to select an output folder.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            if self.check_valid_output_folder(folder):
                self.output_folder = folder
                self.output_folder_label.setText("Output Folder: " + self.output_folder)

    def add_connections(self):
        """
        Connect UI signals to their corresponding slots.
        """
        self.folder_button.clicked.connect(self.select_folders)
        self.output_button.clicked.connect(self.select_output_folder)

    def get_row_count(self):
        """
        Get the number of rows in the folder table.

        :return: Number of rows in the folder table.
        :rtype: int
        """
        if self.folder_table.rowCount() == 0:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("No Folders Selected")
            msg_box.setText("Please select folders containing DPX Sequences to process")
            msg_box.exec_()
        return self.folder_table.rowCount()

    def get_output_folder(self):
        """
        Get the path of the selected output folder.

        :return: Path of the output folder, or an empty string if not set.
        :rtype: str
        """
        if self.output_folder_label.text() == self.empty_output_folder_text:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Output Folder Not Set")
            msg_box.setText("Please select an output folder for the processed videos to be stored")
            msg_box.exec_()
            return ""
        return self.output_folder

    def show_cancel_dialog(self, log_files):
        """
        Show a dialog to confirm cancellation of the current run.

        :param log_files: Information about the log files.
        :type log_files: str
        :return: True if the user confirms cancellation, False otherwise.
        :rtype: bool
        """
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Cancel")
        dialog.setText(f"Are you sure you want to cancel?\nCancelling this run will stop any unfinished sequences. \n"
                       f"Logs Information:\n{log_files}\nNOTE: Move unfinished sequences present in \n"
                       f"{self.output_folder}/working directory \nback to source before starting a new run")
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        response = dialog.exec_()
        return response == QMessageBox.Yes