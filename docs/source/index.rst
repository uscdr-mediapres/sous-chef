.. USC-DR-RAWCOOKED documentation master file, created by
   sphinx-quickstart on Fri Nov 22 14:04:25 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SousChef
============================================

This is a Python GUI that can be used to parallelize lossless compression of large DPX sequences
using `RAWcooked <https://mediaarea.net/RAWcooked>`_ and
`FFMPEG <https://www.ffmpeg.org/>`_.


SousChef is a user-friendly software package designed for audiovisual archivists and other non-technical users. This tool simplifies the process of converting image sequences (such as frames from a film or digital image sets) into high-quality, lossless video files. With an intuitive graphical user interface (GUI), the package allows users to easily queue and manage multiple transcodes at once, without needing any technical knowledge or experience with command-line tools.

The software leverages RAWCooked, a powerful backend tool for high-efficiency transcoding, and includes optimizations that adjust based on available hardware resources. This ensures that the software performs optimally, whether you are working with a personal workstation or a more powerful server setup. Users can customize their transcoding queue based on project needs, significantly improving workflow efficiency when handling large batches of image sequences.

Key Features:

- **Queue Management**: Seamlessly queue multiple transcodes and manage them simultaneously.
- **Performance Optimization**: Automatically optimizes transcoding performance based on available CPU, GPU, and system resources.
- **Lossless Video Creation**: Converts image sequences into high-quality, lossless video formats, perfect for archival purposes.
- **User-Friendly GUI**: No need for technical knowledge or command-line skills; simply load your image sequences and let the software do the rest.

This tool is ideal for audiovisual archivists, film preservationists, and anyone working with large image datasets who needs an easy-to-use, efficient way to convert sequences into professional-grade video files.


.. note::
   This project is under active development.


Index
------

.. toctree::
   quickstart
   mvp_breakdown
   functions
   contact

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
