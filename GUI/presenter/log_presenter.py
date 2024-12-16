from PyQt5.QtCore import QTimer, QFileSystemWatcher


class LogPresenter:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.file_watcher = QFileSystemWatcher()  # Watches for file changes
        self.timer = QTimer()  # Fallback timer for polling
        self.timer.timeout.connect(self.update_log)
        self.file_watcher.fileChanged.connect(self.file_changed)  # Detect file changes

    def start_tailing_log(self):
        """Starts reading the log and watching for changes."""
        file_path = self.model.filepath
        initial_content = self.model.read_new_content()
        self.view.append_log_content(initial_content)
        self.file_watcher.addPath(file_path)
        self.timer.start(100)  # Fallback timer every 1 second

    def update_log(self):
        """Fallback to poll the log for changes every second."""
        new_content = self.model.read_new_content()
        if new_content:
            self.view.append_log_content(new_content)

    def file_changed(self, path):
        """Handles the event when the log file is modified externally."""
        # print(f"File changed: {path}")
        new_content = self.model.read_new_content()
        if new_content:
            self.view.append_log_content(new_content)

    def stop_tailing(self):
        """Stops the log tailing process."""
        self.timer.stop()
        self.file_watcher.removePaths(self.file_watcher.files())
        self.model.close()
