MVP Pattern
===========

Summary
---------------
The GUI follows the Model-View-Presenter(MVP) pattern to isolate the view from the underlying scripts.
The modules are divided into `model`, `view` and `presenter` which contains separate classes.
The following documentation explains the classes and methods used to build the GUI.

Model Overview
--------------

Model Class Overview
~~~~~~~~~~~~~~~~~~~~

Here is a quick overview of the methods and special members defined in the main `Model` class:

.. autoclass:: model.model.Model
   :members:
   :undoc-members:
   :private-members:
   :special-members: __init__
   :show-inheritance:

Log Model Class Overview
~~~~~~~~~~~~~~~~~~~~~~~~

Here is a quick overview of the methods and special members defined in the `LogModel` class:

.. autoclass:: model.log_model.LogModel
   :members:
   :undoc-members:
   :private-members:
   :special-members: __init__
   :show-inheritance:

Progress Bar Model Class Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is a quick overview of the methods and special members defined in the `ProgressBarModel` class:

.. autoclass:: model.progress_bar_model.ProgressBarModel
   :members:
   :undoc-members:
   :private-members:
   :special-members: __init__
   :show-inheritance:

View Overview
-------------