"""
Jupyter Notebook configuration override.
Disables the banner prompting users to update to Jupyter Notebook 7 when running version 6.5.4.
"""
from notebook._version import __version__ as notebook_version

if notebook_version == "6.5.4":
    # Disable banner
    c.NotebookApp.show_banner = False # type: ignore # noqa: F821
