# e2x Prefect Notebook

This Docker image is a customized version of the [e2x Code Notebook](../datascience-notebook-code) image (Data Science Notebook plus VS Code), with [Prefect](https://www.prefect.io/) installed for building and running data pipelines.

## Description

This image is designed for courses on workflow orchestration. It includes:

* All features from the e2x Code Notebook image (Data Science Notebook plus VS Code)
* Prefect, including its server and web dashboard
* `start-prefect`, a script that runs the Prefect server behind the notebook's proxy, so the dashboard opens in the browser
* `start-datacontract-editor`, a script that runs the [Data Contract Editor](https://cli.datacontract.com/) (`datacontract edit`) behind the notebook's proxy

## Starting the Prefect server

Open a terminal (in VS Code or Jupyter) and run:

```bash
start-prefect
```

The script prints the dashboard path (`/user/<name>/proxy/absolute/4200/`); open it on your hub's address. The `127.0.0.1` links Prefect prints itself only work inside the container.
The path comes from `JUPYTERHUB_SERVICE_PREFIX`. Prefect writes its UI files to `PREFECT_UI_STATIC_DIRECTORY` (default `/tmp/prefect-ui`), because the notebook user may not be allowed to write to `site-packages`.

## Starting the Data Contract Editor

Open a terminal and run, with any `datacontract edit` options:

```bash
start-datacontract-editor my-contract.odcs.yaml --language de
```

The script prints the editor path (`/user/<name>/proxy/4243/`); open it on your hub's address. The `localhost:4243` link the editor prints itself only works inside the container.
Plain `datacontract edit` does not work here: its page loads files from root paths, which miss the proxy prefix. The script rewrites them to relative paths.

## Usage

See [Images](../../../README.md#images), [Pull and Run](../../../README.md#pull-and-run)
and [Building Locally](../../../README.md#building-locally) in the main README.
