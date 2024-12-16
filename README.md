# OUTDATED (needs update)
# Rawcooked Workflow
The CLI and GUI Scripts of Rawcooked workflow.

#### GUI Development Notes

The GUI is still in a very early stage of development and is planned to be implemented using PyQt5. I have used the following resources for development:

- PyQt5 Documentation: [Link](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- PyQt5 Slots and Signals Architecture: [Link](https://www.pythonguis.com/tutorials/pyqt-signals-slots-events/)
- PyQt5 Multithreading and inter-thread communication: [Link](https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/)
- PyQt5 Multiprocessing: [Link](https://www.pythonguis.com/tutorials/qprocess-external-programs/)
- PyQt5 Toggle Button: [Link](https://www.pythonguis.com/widgets/pyqt-toggle-widget/)

We have also decided to create GUI-coupled scripts separate from the CLI workflow. All the Python scripts (including thread/process workers) should be created inside `GUI/scripts` and all the reusable UI components should be created inside the `GUI/components`. Execute the `GUI/main.py` to start the GUI application.

## Working Directory Structure
<pre><font color="#3465A4"><b>root_folder</b></font>
├── <font color="#3465A4"><b>media</b></font>
│&nbsp;   ├── <font color="#3465A4"><b>preprocessing</b></font>
│&nbsp;   │&nbsp;   ├── <font color="#3465A4"><b>dpx_gap_check</b></font>
│&nbsp;   │&nbsp;   └── <font color="#3465A4"><b>dpx_policy_check</b></font>
│&nbsp;   ├── <font color="#3465A4"><b>rawcook</b></font>
│&nbsp;   │&nbsp;   ├── <font color="#3465A4"><b>dpx_to_cook</b></font>
│&nbsp;   │&nbsp;   ├── <font color="#3465A4"><b>dpx_to_cook_v2</b></font>
│&nbsp;   │&nbsp;   └── <font color="#3465A4"><b>mkv_cooked</b></font>
│&nbsp;   └── <font color="#3465A4"><b>review</b></font>
│&nbsp;       ├── <font color="#3465A4"><b>failed</b></font>
│&nbsp;       │&nbsp;   ├── <font color="#3465A4"><b>gap_check_failures</b></font>
│&nbsp;       │&nbsp;   ├── <font color="#3465A4"><b>dpx_policy_failures</b></font>
│&nbsp;       │&nbsp;   ├── <font color="#3465A4"><b>mkv_policy_failures</b></font>
│&nbsp;       │&nbsp;   └── <font color="#3465A4"><b>rawcook_failures</b></font>
│&nbsp;       └── <font color="#3465A4"><b>completed</b></font>
│&nbsp;           └── <font color="#3465A4">&lt;folder_name&gt;</font>
│&nbsp;               ├── <font color="#3465A4"><b>sequences</b></font>
│&nbsp;               └── <font color="#3465A4"><b>encoded</b></font>
├── <font color="#3465A4"><b>logs</b></font>
│&nbsp;   ├── <font color="#3465A4"><b>dpx_assessment.log</b></font>
│&nbsp;   ├── <font color="#3465A4"><b>dpx_post_rawcook.log</b></font>
│&nbsp;   └── <font color="#3465A4"><b>dpx_rawcook.log</b></font>
└── <font color="#3465A4"><b>policy</b></font>
 &nbsp;   ├── <font color="#3465A4"><b>dpx_policy.xml</b></font>
 &nbsp;   └── <font color="#3465A4"><b>mkv_policy.xml</b></font>
</pre>

## Environment Variables

These environment variables are used to configure the paths for different folders and files in the script:
- `FILM_OPS`: Path to root media folder.
- `SCRIPT_LOGS`: Relative path to the logs folder.
- `PREPROCESSING`: Relative path to the preprocessing folder.
- `RAWCOOKED`: Relative path to the main RAWCOOKED folder.
- `POLICY_DPX`: Relative path to the XML file containing DPX policy.
- `POLICY_MKV`: Relative path to the XML file containing MKV policy.
- `DPX_GAP_CHECK`: Relative path to the folder containing unassessed DPX sequences to check for gaps.
- `DPX_POLICY_CHECK`: Relative path to the folder containing unassessed DPX sequences to check DPX policy.
- `DPX_TO_COOK`: Relative path to the folder containing DPX files to be cooked.
- `DPX_TO_COOK_V2`: Relative path to the folder containing DPX files to be cooked using output V2.
- `MKV_COOKED`: Relative path to the folder containing cooked files.
- `DPX_GAP_CHECK_FAILED`: Relative path to the folder containing sequences with gaps.
- `DPX_POLICY_CHECK_FAILED`: Relative path to the folder containing sequences not conforming to DPX policy.
- `MKV_POLICY_CHECK_FAILED`: Relative path to the folder containing MKV files not conforming to MKV policy.
- `RAWCOOKED_FAILED`: Relative path to the folder containing files caused by RAWCOOKED script errors.
- `POST_RAWCOOKED_FAILED`: Relative path to the folder containing files caused by post-RAWCOOKED script errors.
- `MKV_COMPLETED`: Relative path to the folder containing DPX sequences already processed.  
**NOTE: Relative paths are relative to FILM_OPS. If changes are made to the relative paths, do not run workflow generator. Instead, create your own directory structure.**

## Setup
To get started, please follow these steps to set up the necessary environment variables and run the scripts:

1. **Clone the Repository**: Start by cloning the project repository to your local machine using Git:

    ```bash
    git clone https://github.com/saiprasa-usc/rawcooked_usc-dr.git
    ```
2. **Rename `.env.example` to `.env`**: In the root directory of the cloned repository, you will find a file named `.env.example`. Rename this file to `.env`. This file will hold your environment variables.

    ```bash
    mv .env.example .env
    ```
3. **Fill in the FILM_OPS variable**: Open the `.env` file in a text editor of your choice. You will see a list of environment variables. Replace the placeholder for the FILM_OPS variable with the actual path to the root working folder of the project. **NOTE: This folder does not have to be where the code is located. It is the path where the dpx_sequences and mkv_files will be processed/**

    Example:
    ```
    FILM_OPS=<path-to-working-directory>
    ...
    ...
    ```
   Replace with:
   ```
    FILM_OPS=/home/user/Desktop/rawcooked_working_folder
    ...
    ...
    ```
4. **Save the Changes**: Once you've filled in all the necessary variables, save the `.env` file.
5. Execute the command below from the terminal to install the dependencies.
   ```
   pip3 install -r requirements.txt
   ``` 

7. **Run the workflow generator script (If directories not already made in the working folder)**: If this is the first time running these scripts in a particular working directory, you need to run the workflow generator script to create all the subdirectories as indicated in the directory structure above. Otherwise, skip to step 6.

8. **Move the dpx sequences to the correct processing folder**: If the dpx sequences need preprocessing before running rawcooked, they need to be moved to the required preprocessing folder as indicated below:  
**media/preprocessing/dpx_gap_check (Recommended)** - Check dpx sequences for possible gaps leading to incoherent sequences  
**media/preprocessing/dpx_policy_check** - Check whether the dpx_sequences match the dpx_policy specified in the policy/ folder. Files are automatically moved here after gap checking.  
**media/rawcooked/dpx_to_cook** - If no preprocessing is needed. Files in preprocessing folders will automatically be moved here once necessary checks pass.  
**media/rawcooked/dpx_to_cook_v2** - In no preprocessing is needed and file needs to be cooked with rawcooked output-version-2. Files are automatically moved here if reversibility file becomes too large during preprocessing checks

9. **Move the policy files to the policy folder**: The policy files to compared against for both dpx and mkv files should be placed in the policy folder and named as below:  
**dpx_policy** - rawcooked_dpx_policy.xml  
**mkv_policy** - rawcooked_mkv_policy.xml
10. **Run the main processing script**:  Once all the dpx sequences are moved to their correct folders, we need to run the shell script ```run.sh```. This will call the python scripts as specified in the workflow below. To run this from the terminal:  
   ```bash
   chmod +x run.sh
   ```
   ```bash
   ./run.sh
   ```
11. **Review Files**: Once the scripts are done executing, all processed sequences will be moved to the review folder. The **review/completed** folder will have successfully cooked mkv files, mkv.txt files, dpx sequences and checksum files. If the dpx/mkv files fail for any reason they will be present in the **/review/failed** folder.



## Workflow

Three Scripts:

- dpx_assessment.py
- dpx_rawcook.py
- dpx_post_rawcook.py

### dpx_assessment
- reads dpx_to_assess folder
- runs media conch policy checks on the sequences in this folder
- runs rawcooked --no-encode on the sequences to check for gaps or large reversibility files
- moves sequences with gaps to dpx_to_review >> dpx_with_gaps
- moves sequences with larger reversibility files to dpx_to_cook_v2
- moves the remaining sequences to dpx_to_cook

### dpx_rawcook.py
- runs rawcooked for sequences in dpx_to_cook folder and moves the mkvs to mkv_cooked folder
- runs rawcooked with output version 2 for sequences in dpx_to_cook_v2 folder and moves the mkvs to mkv_cooked_v2 folder
- moves failed files to dpx_to_review > rawcooked_failed or dpx_to_review > rawcooked_v2_failed

### dpx_post.py
- runs mediaconch policy checks on the mkv files in the cooked folders
- moves fails to mkx_to_review > mediaconch_fails
- moves successfully dpx sequences to dpx_completed folder
- check general errors, stalled encodings and incomplete cooks (TODO: decide folder structure)

## Logging
- three log files for each script
- overall log
- success log
- failure log
