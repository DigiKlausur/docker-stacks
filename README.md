[![K8s Hub](https://github.com/DigiKlausur/docker-stacks/actions/workflows/hub.yml/badge.svg)](https://github.com/DigiKlausur/docker-stacks/actions/workflows/hub.yml)

[![Notebook Stable](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_main.yml/badge.svg)](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_main.yml)
[![Notebook Dev](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_dev.yml/badge.svg)](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_dev.yml)

# E2x Docker Stacks

Ready to run docker images of the `e2x` project for various use cases. 
All images are hosted on `ghcr.io` and `quay.io`.

## Hub

All [hub images](hub) contain JupyterHub, [e2xhub](https://github.com/DigiKlausur/e2xhub), as well as authenticators.

## Jupyter Notebook Images

There are several Jupyter Notebook images for different use cases.
Currently all images are based on `notebook==6.5.4`.

| Image                | Base                                                                   | Teacher                                                                           | Student                                                                           | Exam                                                                        |
|----------------------|------------------------------------------------------------------------|-----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| [minimal-notebook](notebooks/images/minimal-notebook)     | [base](https://ghcr.io/digiklausur/docker-stacks/minimal-notebook)     |                                                                                   |                                                                                   |                                                                             |
| [datascience-notebook](notebooks/images/datascience-notebook) | [base](https://ghcr.io/digiklausur/docker-stacks/datascience-notebook) | [teacher](https://ghcr.io/digiklausur/docker-stacks/datascience-notebook-teacher) | [student](https://ghcr.io/digiklausur/docker-stacks/datascience-notebook-student) | [exam](https://ghcr.io/digiklausur/docker-stacks/datascience-notebook-exam) |
| [ml-notebook](notebooks/images/ml-notebook) | [base](https://ghcr.io/digiklausur/docker-stacks/ml-notebook) | [teacher](https://ghcr.io/digiklausur/docker-stacks/ml-notebook-teacher) | [student](https://ghcr.io/digiklausur/docker-stacks/ml-notebook-student) | [exam](https://ghcr.io/digiklausur/docker-stacks/ml-notebook-exam) |
| [nlp-notebook](notebooks/images/nlp-notebook) | [base](https://ghcr.io/digiklausur/docker-stacks/nlp-notebook) | [teacher](https://ghcr.io/digiklausur/docker-stacks/nlp-notebook-teacher) | [student](https://ghcr.io/digiklausur/docker-stacks/nlp-notebook-student) | [exam](https://ghcr.io/digiklausur/docker-stacks/nlp-notebook-exam) |
| [sql-notebook](notebooks/images/sql-notebook) | [base](https://ghcr.io/digiklausur/docker-stacks/sql-notebook) | [teacher](https://ghcr.io/digiklausur/docker-stacks/sql-notebook-teacher) | [student](https://ghcr.io/digiklausur/docker-stacks/sql-notebook-student) | [exam](https://ghcr.io/digiklausur/docker-stacks/sql-notebook-exam) |
| [julia-notebook](notebooks/images/julia-notebook) | [base](https://ghcr.io/digiklausur/docker-stacks/julia-notebook) | [teacher](https://ghcr.io/digiklausur/docker-stacks/julia-notebook-teacher) | [student](https://ghcr.io/digiklausur/docker-stacks/julia-notebook-student) | [exam](https://ghcr.io/digiklausur/docker-stacks/julia-notebook-exam) |
| [desktop-notebook](notebooks/images/desktop-notebook)     | [base](https://ghcr.io/digiklausur/docker-stacks/desktop-notebook)     |                                                                                   |                                                                                   |                                                                             |

The notebook images are:

* [Minimal Notebook](notebooks/images/minimal-notebook/): Base image used for all other images here.
* [Data Science Notebook](notebooks/images/datascience-notebook/): Based on Minimal Notebook. Additional Python data science libraries (e.g., numpy, scipy, pandas, sklearn, statsmodels). 
* [Machine Learning Notebook](notebooks/images/ml-notebook/): Based on Data Science Notebook. Additional Python machine learning libraries (e.g., pytorch, gymnasium). 
* [Natural Language Processing Notebook](notebooks/images/nlp-notebook/): Based on Machine Learning Notebook. Additional Python NLP libraries (e.g., nltk, spacy, gensim, transformers). 
* [SQL Notebook](notebooks/images/sql-notebook/): Based on Data Science Notebook. Additional SQL libraries and kernels.
* [Julia Notebook](notebooks/images/julia-notebook/): Based on Minimal Notebook. Adds a Julia kernel and libraries.
* [Desktop Notebook](notebooks/images/desktop-notebook/): Based on Minimal Notebook. Customized version of the [Minimal Notebook](notebooks/images/minimal-notebook) image, with an XFCE desktop installed using [Jupyter Remote Desktop Proxy](https://github.com/jupyterhub/jupyter-remote-desktop-proxy).
* [DB Main Notebook (experimental)](notebooks/images/dbmain-notebook/): Based on Desktop Notebook. With the DB Main application installed. Serves as an example for running an application in a desktop image.

## E2xGrader Images

Each end-point image comes in four different flavors:

* Vanilla: Basic image without any e2xgrader extensions.
* Teacher: Includes `e2xgrader` with teacher mode activated and is intended for instructors for creating and grading assignments.
* Student: Includes `e2xgrader` with student mode activated and is intended for students for working on assignments.
* Exam: Includes `e2xgrader` with student_exam mode activated and is intended for students for working on exams, providing a restricted notebook.

## Build Tree

The following diagram illustrates the dependencies between the different images:

![build tree](architecture.png)

## Building Locally

All images are defined in [`notebooks.toml`](notebooks.toml). The script in
[`scripts/image_builder`](scripts/image_builder) reads it. It only needs Docker and Python ≥ 3.11,
with no packages to install.

```bash
# Show which image builds on which
python scripts/image_builder tree

# Build one image → ghcr.io/digiklausur/docker-stacks/ml-notebook:local
python scripts/image_builder build ml-notebook

# e2xgrader variants are images of their own
python scripts/image_builder build ml-notebook-student

# An image and everything below it, each on its fresh :local parent
python scripts/image_builder build datascience-notebook --with-dependents

# Every image, in build order
python scripts/image_builder build --all

# Only print the docker command(s)
python scripts/image_builder build ml-notebook --dry-run

# Try another e2xgrader version, or install it from a GitHub branch
python scripts/image_builder build ml-notebook-student --build-arg E2XGRADER_VERSION=0.4.0
python scripts/image_builder build ml-notebook-student \
    --build-arg FROM_REPO=true --build-arg E2XGRADER_BRANCH=dev

# Run a locally built image
docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/ml-notebook:local

# See what CI would build for the changes on your branch
python scripts/image_builder plan --tag-set dev --since origin/dev
```

- Results are tagged `:local` and never pushed. A parent built in the same call is used as `:local`;
  any other parent is pulled from the registry (tag `latest`).
- To add an image, create `notebooks/images/<name>/` and add an `[images.<name>]` entry to
  `notebooks.toml`. Run `python scripts/image_builder tree` to check it.
- Tests: `pip install pytest`, then `python -m pytest`.

## Branches

The `dev` branch will always reflect `ghcr.io/digiklausur/docker-stacks/{image_name}:dev` on the GitHub container registry, and the `master` branch reflects `ghcr.io/digiklausur/docker-stacks/{image_name}:latest`. 

## Contributing

If you'd like to contribute to this repository, please feel free to open an issue or submit a pull request.

## License

The images in this repository are licensed under MIT.
