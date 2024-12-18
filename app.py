import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from GUI.model.model import Model
from GUI.view.preferences_view import PreferencesView
from GUI.view.view import View
from GUI.presenter.presenter import Presenter

if __name__ == "__main__":
    app = QApplication(sys.argv)

    script_dir = Path(__file__).resolve().parent

    default_cores = os.cpu_count()

    model = Model(script_dir)
    if not model.config_exists():
        config_dialog = PreferencesView(max_cores = default_cores, selected_cores=default_cores)
        if config_dialog.exec_() == config_dialog.Accepted:
            config_data = config_dialog.get_config_data()
            model.save_config(config_data)
        else:
            sys.exit(0)
    view = View(script_dir)
    presenter = Presenter(model, view)
    view.show()
    sys.exit(app.exec_())
