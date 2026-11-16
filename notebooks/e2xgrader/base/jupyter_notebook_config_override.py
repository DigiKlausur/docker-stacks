"""
Jupyter Notebook configuration override.
Disables the banner prompting users to update to Jupyter Notebook 7.
"""
from notebook._version import __version__ as notebook_version

c.NotebookApp.show_banner = False # type: ignore # noqa: F821
