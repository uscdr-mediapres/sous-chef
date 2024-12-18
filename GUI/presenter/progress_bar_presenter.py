from PyQt5.QtCore import QTimer, QFileSystemWatcher, pyqtSignal, QObject


class ProgressPresenter(QObject):
    progress_ended = pyqtSignal(str)

    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view
        model.progress_error.connect(view.update_progress_bar)
        self.file_watcher = QFileSystemWatcher()  # Watches for file changes
        self.timer = QTimer()  # Fallback timer for polling
        self.timer.timeout.connect(self.update_progress)
        self.file_watcher.fileChanged.connect(self.file_changed)  # Detect file changes

    def start_tailing_log(self):
        """Starts reading the log and watching for changes."""
        # Add the file path to the watcher
        file_path = self.model.filepath
        if file_path:
            self.file_watcher.addPath(file_path)
        # Start fetching initial data to prime the progress bar
        self.update_ui_with_data()

        # Start the fallback timer
        self.timer.start(1000)  # Poll every 100 ms

    def update_progress(self):
        """Fetch new data and update the progress bar and section label."""
        self.update_ui_with_data()

    def cancel_progress(self):
        """Fetch new data and update the progress bar and section label."""
        self.update_ui_with_data()

    def file_changed(self, path):
        """Handles the event when the log file is modified externally."""
        # Fetch and process new data when the file changes
        self.update_ui_with_data()

    def update_ui_with_data(self, cancel_str=""):
        if cancel_str != "":
            self.view.section_label.setText("CANCELLED")
            self.view.update_progress_bar("Process Cancelled", 100)
            self.timer.stop()
            return

        """Updates the UI components with new data."""
        raw_content = self.model.read_new_content()
        for line in raw_content.splitlines():
            if line != "":
                new_data = self.model.fetch_data(line)
                section = new_data.get("section", "ERROR")
                if section != "ERROR":
                    self.view.section_label.setText(section)

                    # Stop the timer if the task is completed
                    if section == "COMPLETED":
                        self.view.update_progress_bar(new_data["progress"].get("name", "Unknown"), 100)
                        self.timer.stop()
                        print(f"Ended:{self.view.filename}")
                        self.progress_ended.emit(self.view.filename)
                        return
                else:
                    self.view.section_label.setText("ERROR")
                    self.view.update_progress_bar("Error Occurred. Check log files", 100)
                    self.timer.stop()
                    return

                # Update the progress bar with dynamic content
                progress_name = new_data["progress"].get("name", "Unknown")
                progress_value = float(new_data["progress"].get("value", 0))
                self.view.update_progress_bar(progress_name, progress_value)

    def stop_tailing(self):
        """Stops the log tailing process."""
        self.timer.stop()
        self.file_watcher.removePaths(self.file_watcher.files())
        self.model.close_file()  # Ensure the model's file is properly closed
