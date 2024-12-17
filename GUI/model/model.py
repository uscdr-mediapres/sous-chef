import json
import os
import subprocess
import time

import psutil


class Model:
    """
    """

    def __init__(self, project_root):
        self.project_root = project_root
        self.backend_config_folder = project_root / "config"
        self.create_config_folder()
        self.app_config_path = project_root / "app_config.json"
        self.log_config_file = os.path.join(self.backend_config_folder, "log_config.json")
        self.num_sequences = 0
        self.license = ""
        self.cpu_cores = os.cpu_count()
        self.process = None

    def config_exists(self) -> bool:
        return self.app_config_path.exists()

    def load_config(self) -> dict:
        if not self.config_exists():
            return {}
        with open(self.app_config_path, "r") as file:
            return json.load(file)

    def save_config(self, config: dict):
        with open(self.app_config_path, "w") as file:
            json.dump(config, file, indent=4)

    def clean_config_folder(self):
        for file in os.listdir(self.backend_config_folder):
            os.remove(os.path.join(self.backend_config_folder, file))

    def read_app_config(self):
        """ """
        try:
            with open(self.app_config_path, "r") as config_file:
                config = json.load(config_file)
                self.license = config.get("RAWCOOKED_LICENSE_VERSION", "No license information")
                self.cpu_cores = config.get("CPU_CORES", os.cpu_count())
        except (FileNotFoundError, json.JSONDecodeError):
            self.cpu_cores = os.cpu_count()  # Default to all available cores
            return "Config file read error"

    def get_license_config(self):
        """ """
        self.read_app_config()
        return self.license

    def get_cpu_cores(self):
        """ """
        self.read_app_config()
        return self.cpu_cores

    def write_license(self, license_version):
        """Write or remove the license version in the configuration file.

        :param license_version: 

        """
        try:
            with open(self.app_config_path, "r") as config_file:
                config = json.load(config_file)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        if license_version:  # Set or update the license
            config["RAWCOOKED_LICENSE_VERSION"] = license_version
        else:  # Remove the license
            config["RAWCOOKED_LICENSE_VERSION"] = ""

        with open(self.app_config_path, "w") as config_file:
            json.dump(config, config_file, indent=4)

    def set_cpu_cores(self, cores):
        """Update the number of CPU cores in the configuration file.

        :param cores: 

        """
        try:
            with open(self.app_config_path, "r") as config_file:
                config = json.load(config_file)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        config["CPU_CORES"] = cores
        self.cpu_cores = cores

        with open(self.app_config_path, "w") as config_file:
            json.dump(config, config_file, indent=4)

    def set_policy(self, policy_name, policy_path):
        """
        Set or update the specified policy file path in the configuration.

        :param policy_name: Name of the policy (e.g., "DPX_POLICY", "MKV_POLICY")
        :param policy_path: File path to the policy
        """
        config = self.load_config()
        if policy_path:
            config[policy_name] = policy_path
        else:
            config.pop(policy_name, None)
        self.save_config(config)

    def read_policy(self, policy_name):
        """

        :param policy_name: 

        """
        try:
            with open(self.app_config_path, "r") as config_file:
                config = json.load(config_file)
                return config.get(policy_name, "No policy specified for: " + policy_name)
        except FileNotFoundError:
            return "Config file not found"
        except json.JSONDecodeError:
            return "Error reading config file"

    def create_driver_config(self, output_folder_path, num_sequences):
        """

        :param output_folder_path: param num_sequences:
        :param num_sequences: 

        """
        self.num_sequences = num_sequences
        driver_data = {"output_folder_path": output_folder_path,
                       "sequence_count": self.num_sequences,
                       "cpu_affinity": self.get_cpu_cores()
                       }
        print("Current working directory:", os.getcwd())
        driver_config_file = os.path.join(self.backend_config_folder, "driver_config.json")
        with open(driver_config_file, "w") as json_file:
            json.dump(driver_data, json_file, indent=4)
        print("Data saved to: driver_config.json")
        return driver_config_file

    def create_worker_config(self, row_index, row_data):
        """

        :param row_index: param row_data:
        :param row_data: 

        """
        if self.license == "":
            self.read_app_config()
        row_data.update({"license": self.license})

        sequence_config_file = os.path.join(self.backend_config_folder, f"sequence_{row_index}.json")
        with open(sequence_config_file, "w") as json_file:
            json.dump(row_data, json_file, indent=4)
            print(f"Data saved to: {sequence_config_file}")

    def get_sequence_name(self, seq_num):
        """

        :param seq_num: 

        """
        sequence_config_file = os.path.join(self.backend_config_folder, f"sequence_{seq_num}.json")
        with open(sequence_config_file, "r") as json_file:
            seq_configs = json.load(json_file)
        return seq_configs["sequence_folder_path"]

    def get_log_files(self):
        """ """
        with open(self.log_config_file, "r") as json_file:
            log_configs = json.load(json_file)
        seq_log_map = {}
        for worker_num, worker_log_files in log_configs["workers"].items():
            seq_name = self.get_sequence_name(worker_num)
            debug_log_file = worker_log_files["debug"]
            info_log_file = worker_log_files["info"]
            seq_log_map[seq_name] = (debug_log_file, info_log_file)
        return seq_log_map

    def run(self):
        """ """
        driver_script = self.project_root / "scripts" / "driver.py"
        self.process = subprocess.Popen(['python', driver_script, '--config', f'{self.backend_config_folder}'],
                                        stdout=subprocess.PIPE, text=True)
        while not os.path.exists(self.log_config_file):
            print("Waiting for logs")
            time.sleep(1)
        return self.get_log_files()

    def create_config_folder(self):
        if not os.path.exists(self.backend_config_folder):
            os.mkdir(self.backend_config_folder)

    def cancel(self):
        if self.process:
            self.process.terminate()
        try:
            self.process.wait(timeout=5)  # Wait for process to exit
        except subprocess.TimeoutExpired:
            print("Force killing backend process...")
            self.process.kill()  # Force kill if not terminated
        else:
            print("No backend process is running.")