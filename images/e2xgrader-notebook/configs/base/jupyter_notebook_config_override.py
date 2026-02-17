from notebook._version import __version__ as notebook_version # type: ignore

if notebook_version == "6.5.4":
    # Disable banner
    c.NotebookApp.show_banner = False # noqa: F821 # type: ignore
