# SousChef

An easy-to-use application that encodes DPX sequences into MKV video streams, primarily for archival storage.
The application is built on Python 3.8 and uses FFMPEG, RAWcooked and MediaConch. Basic installation
and usage instructions are listed below, our [docs](https://souschef.readthedocs.io/en/latest/index.html) provide a detailed
explanation of this implementation.

### Requirements

SousChef is currently only available on Linux systems, and was built on Ubuntu-20.04. Listed below are the pre-requisites to execute: 
- Python 3.8 (or higher), available on `/bin/python3`
- the `psutil` library installed on Python
  - run `pip install psutil`
  - verify the installation by running `pip freeze | grep psutil`, which should show the version number
- FFMPEG (download [here](https://www.ffmpeg.org/download.html))
- RAWcooked (download [here](https://mediaarea.net/RAWcooked/Download))
- MediaConch (download [here](https://mediaarea.net/MediaConch/Download))


### Installation

Choose the latest tag on the GitHub page (currently `v0.1`) and go to the `Releases` section. Click on SousChef under
the Assets section to download the application. The source code is also available in this section but not required to
run the program. 

Finally run `chmod +x SousChef` to provide permissions. 


### Usage

The first time the program is run, it prompts you for the default DPX and MKV policy files, as well as a RAWcooked license. 
These are optional and can be skipped based on your use case. They can also be altered later under the `Preferences` tab. The opening
prompt also contains a slider for the number of cores to use for the encoding process. The recommended value is 75-80% of the maximum value. 

Follow these steps on the main window to cook a sequence:
- click on `Select Folders to Cook` to select sequence folders. Of note, the DPX sequence can be at any depth
within this folder, and the accompanying audio file is optional.
- click on `Select Output Folder` to select the output destination. This folder will contain the final MKV file,
execution logs, and verification files.
- select the appropriate options for each loaded sequence (gap checks, policy checks, md5 checks). The `Process In-Place`
is selected by default and is the recommended option for large sequences or critical data. If this option is not selected,
the data could be lost in case of an unexpected crash.
- click `Run`

The window on the bottom shows the progress of each sequence and the current stage of execution. The window on the right shows
the running logs, and can help in case of errors.

Once the execution is complete, all relevant files can be found in the selected output folder. For a detailed explanation
of the file structure, check out the [documentation](https://souschef.readthedocs.io/en/latest/index.html).