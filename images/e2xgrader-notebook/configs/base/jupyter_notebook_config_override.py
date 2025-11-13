from notebook._version import __version__ as notebook_version
import os

if notebook_version == "6.5.4":
    # Disable banner
    c.NotebookApp.show_banner = False
