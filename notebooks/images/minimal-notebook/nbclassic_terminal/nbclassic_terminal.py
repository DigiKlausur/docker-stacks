"""
Serve nbclassic's terminal page at <base_url>/nbclassic/terminals/<name>.

nbclassic registers its terminal page at /terminals/<name>, but Notebook 7 serves
that route first, and Notebook 7's logo leads to /tree. With this route, terminals
opened from nbclassic stay in nbclassic (see custom-preload.js).
Remove once e2xgrader runs on Notebook 7.
"""

from jupyter_server.utils import url_path_join
from nbclassic.terminal.handlers import TerminalHandler


def _jupyter_server_extension_points():
    return [{"module": "nbclassic_terminal"}]


def _load_jupyter_server_extension(serverapp):
    route = url_path_join(serverapp.base_url, r"/nbclassic/terminals/(\w+)")
    serverapp.web_app.add_handlers(
        ".*$", [(route, TerminalHandler, {"name": "nbclassic"})]
    )
