Functions
======================

Summary
---------------

Each sequence is processed in three stages:

- `DPX Assessment`_: validity checks on the DPX sequence before processing
- `DPX Rawcook`_: the cooking process handled by RAWcooked
- `DPX Post Rawcook`_: validity checks on the MKV, file cleanup and error reporting

The parameters and working of the operations in these stages are listed below.
The `Utils`_ section contains utility functions used across each stage to setup
file structures, setup logging, verify policies or move/copy sequences.


DPX Assessment
----------------
.. autofunction:: dpx_assessment.execute
.. autofunction:: dpx_assessment.check_v2
.. autofunction:: dpx_assessment.check_gap

DPX Rawcook
------------
.. autofunction:: dpx_rawcook.execute
.. autofunction:: dpx_rawcook.run_rawcooked
.. autofunction:: dpx_rawcook.grep_with_redirect

DPX Post Rawcook
------------------
.. autofunction:: dpx_post_rawcook.execute

Utils
-------

.. autofunction:: utils.create_execution_dir
.. autofunction:: utils.create_working_dir
.. autofunction:: utils.get_log_config
.. autofunction:: utils.move_logs
.. autofunction:: utils.write_log_config
.. autofunction:: utils.find_sequence_path
.. autofunction:: utils.check_mediaconch_policy
.. autofunction:: utils.check_general_errors
.. autofunction:: utils.move
.. autofunction:: utils.copy
.. autofunction:: utils.sequence_count
