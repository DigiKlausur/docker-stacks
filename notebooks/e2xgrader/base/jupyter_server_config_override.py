"""
Jupyter Server configuration override, appended to /etc/jupyter/jupyter_server_config.py.
Server config also applies when JupyterHub runs jupyterhub-singleuser directly.
"""

# Open nbclassic by default (Notebook 7 owns /tree, nbclassic lives under /nbclassic).
# jupyterhub-singleuser ignores DOCKER_STACKS_JUPYTER_CMD, so this is set here.
c.ServerApp.default_url = "/nbclassic/tree"  # type: ignore # noqa: F821

# Only allow embedding the notebook in frames from the same origin
c.ServerApp.tornado_settings = {  # type: ignore # noqa: F821
    "headers": {"Content-Security-Policy": "frame-ancestors 'self'"}
}
