class PreferencesPresenter:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        # Connect View signals to Presenter slots
        self.view.edit_license_clicked.connect(self.on_edit_license_clicked)
        self.view.cpu_cores_changed.connect(self.on_cpu_cores_changed)
        self.view.change_policy_clicked.connect(self.on_change_policy)

        # Initialize license and CPU cores
        self.license_version = self.model.get_license_config()
        self.view.update_license_display(self.license_version)

        self.cpu_cores = self.model.get_cpu_cores()
        self.view.cpu_cores_slider.setValue(self.cpu_cores)
        self.view.cpu_cores_label.setText(f"Number of Cores: {self.cpu_cores}")

    def on_edit_license_clicked(self, new_license, ok):
        """Handle the Edit License button click."""
        if ok:  # User confirmed
            new_license = new_license.strip() if new_license else None
            self.model.write_license(new_license)  # Update the model
            self.license_version = new_license  # Update internal state
            self.view.update_license_display(new_license)  # Update the view

    def on_cpu_cores_changed(self, cores):
        """Handle changes to the CPU cores slider."""
        self.model.set_cpu_cores(cores)  # Update the model
        self.cpu_cores = cores  # Update internal state

    def on_change_policy(self, policy_name, policy_path):
        self.model.set_policy(policy_name, policy_path)
