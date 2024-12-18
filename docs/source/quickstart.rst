Quickstart
===========

Installation
---------------
Install it with the wizard if we make one

..  code-block:: console

    pip install something here
    run some tests here

Execution
-----------
A way to run it maybe with some examples. Show off the GUI


Output
-------
The MKV from the RAWcook, FrameMD5 file, detailed/high-level logs and an mkv.txt for verification checks
can all be found in the output folder specified by the user through the GUI. Every sequence output is written
to the same output folder. An example output for 2 sequences is shown below:

.. code-block:: text

    {output_folder_from_GUI}
    └── execution_{timestamp}
        ├── sequence_1.mkv
        ├── sequence_2.mkv
        ├── sequence_1.framemd5
        ├── sequence_2.framemd5
        ├── sequence_1.mkv.txt
        ├── sequence_2.mkv.txt
        ├── debug.log
        ├── error.log
        ├── info.log
        └── logs
            ├── sequence_1
            │   ├── debug.log
            │   ├── error.log
            │   └── info.log
            └── sequence_2
                ├── debug.log
                ├── error.log
                └── info.log

All outputs of an execution are within the :code:`execution_{timestamp}` folder.
The timestamp is in the YYYY_MM_DD_HH_MM format (eg. :code:`execution_2024_11_15_13_33`).
It is possible to run multiple executions in the same output folder, however they cannot
be run simultaneously.

The logs in the execution folder are a high level overview of the entire execution.
The logs in the :code:`logs` folder are specific to each sequence and provide specific details of
the cooking process. The :code:`info.log` for each specific sequence is displayed
on the GUI during the cooking process.

Monitor
---------

The GUI shows the :code:`info.log` for each sequence during the cooking process. After execution,
the detailed logs for each sequence can be found at :code:`{output_folder}/execution_{timestamp}/logs/`.
The full file structure of logs is listed in `Output`_.
