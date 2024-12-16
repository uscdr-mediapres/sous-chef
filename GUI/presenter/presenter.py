import os.path

from GUI.view.license_view import AboutWindow
from GUI.model.log_model import LogModel
from GUI.view.log_view import LogWidget
from GUI.presenter.log_presenter import LogPresenter
from GUI.presenter.preferences_presenter import PreferencesPresenter
from GUI.model.progress_bar_model import ProgressBarModel
from GUI.view.progress_bar_view import ProgressBarView
from GUI.presenter.progress_bar_presenter import ProgressPresenter
from GUI.view.preferences_dialog import PreferencesDialog


class Presenter:
    def __init__(self, model, view):
        self.driver_config_file = None
        self.preferences_window = None
        self.about_window = None
        self.license_version = None
        self.current_cpu_cores = 0
        self.model = model
        self.view = view
        self.view.about_action.triggered.connect(lambda: self.on_toolbar_action("About Clicked"))
        self.view.pref_action.triggered.connect(lambda: self.on_toolbar_action("Preferences Clicked"))
        self.view.folder_policy_details.connect(self.get_policies_from_config)
        self.folder_table = view.folder_table
        self.get_policies_from_config()
        self.num_sequences = 0
        self.log_presenters = []
        self.progress_presenters = []
        self.preferences_presenter = None
        self.view.run_button.clicked.connect(lambda: self.run_backend())

    def on_toolbar_action(self, action):
        self.license_version = self.model.get_license_config()
        self.current_cpu_cores = self.model.get_cpu_cores()
        if action == "About Clicked":
            self.about_window = AboutWindow("RAWCooked USC DR")
            self.about_window.exec_()
        elif action == "Preferences Clicked":
            self.preferences_window = PreferencesDialog(self.folder_table.default_dpx_policy,
                                                        self.folder_table.default_mkv_policy,
                                                        os.cpu_count(),
                                                        self.current_cpu_cores,
                                                        self.license_version)
            self.preferences_presenter = PreferencesPresenter(self.preferences_window, self.model)
            self.preferences_window.show()

    def get_policies_from_config(self):
        self.folder_table.default_dpx_policy = self.model.read_policy("DPX_POLICY")
        self.folder_table.default_mkv_policy = self.model.read_policy("MKV_POLICY")

    def create_config_files(self):
        self.num_sequences = self.view.get_row_count()
        output_folder = self.view.get_output_folder()
        if self.num_sequences and output_folder != "":
            self.driver_config_file = self.model.create_driver_config(output_folder, self.num_sequences)
            table_data = self.folder_table.get_table_data()
            for row_index, row_data in enumerate(table_data):
                self.model.create_worker_config(row_index, row_data)

    def start_log_widget(self, seq_file_name, log_file_name):
        log_model = LogModel(log_file_name)
        log_view = LogWidget(seq_file_name)
        log_presenter = LogPresenter(log_model, log_view)
        self.log_presenters.append(log_presenter)
        self.view.log_layout.addWidget(log_view)
        log_presenter.start_tailing_log()

    def start_progress_bar_widget(self, seq_file_name, log_file_name):
        progress_model = ProgressBarModel(log_file_name)
        progress_view = ProgressBarView(seq_file_name)
        progress_presenter = ProgressPresenter(progress_model, progress_view)
        self.progress_presenters.append(progress_presenter)
        self.view.progress_layout.addWidget(progress_view)
        progress_presenter.progress_ended.connect(self.on_progress_bar_ended)
        progress_presenter.start_tailing_log()

    def on_progress_bar_ended(self, file_path):
        self.folder_table.delete_row_by_name(file_path)

    def run_backend(self):
        if not os.path.exists(self.model.backend_config_folder):
            self.model.create_config_folder()
        else:
            self.model.clean_config_folder()
        self.create_config_files()
        if self.driver_config_file is not None:
            log_files = self.model.run()
            for seq_name, log_files in log_files.items():
                debug_log_file = log_files[0]
                info_log_file = log_files[1]
                self.start_log_widget(seq_name, info_log_file)
                self.start_progress_bar_widget(seq_name, debug_log_file)
