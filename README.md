[![K8s Hub](https://github.com/DigiKlausur/docker-stacks/actions/workflows/hub.yml/badge.svg)](https://github.com/DigiKlausur/docker-stacks/actions/workflows/hub.yml)

[![Notebook Stable](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_main.yml/badge.svg)](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_main.yml)
[![Notebook Dev](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_dev.yml/badge.svg)](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_dev.yml)

# E2x Docker Stacks

Ready to run docker images of the `e2x` project for various use cases. 
All images are hosted on `ghcr.io` and `quay.io`.

## Hub

All [hub images](hub) contain JupyterHub, [e2xhub](https://github.com/DigiKlausur/e2xhub), as well as authenticators.

## Images

Jupyter Notebook images for different use cases, defined in [`notebooks.toml`](notebooks.toml).
External base images are the roots; each image builds on the one above it.
What an image adds is described in its folder under [`notebooks/images`](notebooks/images).

<!-- tree:start (output of `python scripts/image_builder tree`) -->
```
jupyter/minimal-notebook:notebook-6.5.3
└── bi-notebook [e2x]
jupyter/minimal-notebook:notebook-6.5.4
└── minimal-notebook [e2x]
    ├── bidata-notebook [e2x]
    ├── datascience-notebook [e2x]
    │   ├── datascience-notebook-code [e2x]
    │   ├── ml-notebook [e2x]
    │   │   └── nlp-notebook [e2x]
    │   ├── sql-notebook [e2x]
    │   ├── tf-notebook [e2x]
    │   └── wus-notebook [e2x]
    ├── desktop-notebook
    │   └── dbmain-notebook [e2x]
    └── java-notebook [e2x]
```
<!-- tree:end -->

## E2xGrader Images

Every image marked `[e2x]` also comes in three flavors with [e2xgrader](notebooks/e2xgrader)
installed, named `<image>-<flavor>` (e.g. `ml-notebook-exam`):

* `-teacher`: teacher mode, for instructors creating and grading assignments.
* `-student`: student mode, for students working on assignments.
* `-exam`: student_exam mode, for students working on exams, with a restricted notebook.

## Pull and Run

```bash
docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/<image>:latest
```

* Registries: `ghcr.io` and `quay.io` hold the same images (same digests).
* Tags (defined as tag sets in [`notebooks.toml`](notebooks.toml)):

  | Branch   | Moving tag | Per day (UTC)    | Per commit          |
  |----------|------------|------------------|---------------------|
  | `main`   | `latest`   | `YYYY-MM-DD`     | `sha-<commit>`      |
  | `dev`    | `dev`      | `dev-YYYY-MM-DD` | `dev-sha-<commit>`  |

  Per-commit tags never move, so they are the safest way to pin a course or an exam
  to a fixed set of images. A per-day tag is only updated by later builds on the same day.

## Inspecting an Image

Every image records how it was built in `/etc/image-info.json`: one entry per layer
of the build chain, with its parent, git commit and build time. `image_info` shows it:

```console
$ docker run --rm ghcr.io/digiklausur/docker-stacks/ml-notebook-student:latest image_info
Image:   ml-notebook-student
Built:   2026-11-11T10:40:00+00:00
Commit:  9d8cbe2051c94133673701e988b187d80d887842
...

Build chain (base -> current):
  ·  jupyter/minimal-notebook:notebook-6.5.4  [external base]
  1  minimal-notebook                         built 2026-11-11T10:00:00+00:00  git 9d8cbe2
  2  datascience-notebook                     built 2026-11-11T10:15:00+00:00  git 9d8cbe2
  3  ml-notebook                              built 2026-11-11T10:25:00+00:00  git 9d8cbe2
  4  ml-notebook-student                      built 2026-11-11T10:40:00+00:00  git 9d8cbe2
```

`image_info --json` prints the raw data, `image_info --field git_commit` a single value.
Tags are not recorded, since they are assigned (and moved) after the build.

Installed packages are not recorded; the package managers answer that directly:

```bash
# What is installed
docker run --rm <image> mamba list
docker run --rm <image> pip list

# What changed between two images
diff <(docker run --rm <image>:sha-aaaaaaa pip list --format=freeze) \
     <(docker run --rm <image>:sha-bbbbbbb pip list --format=freeze)

# Which image installs a package: search the repo at a layer's commit
git grep -i numpy 9d8cbe2 -- notebooks/
```

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

# Build on another parent tag instead of `latest`: your own local build,
# or exactly the parent of a CI run (to reproduce a failure)
python scripts/image_builder build minimal-notebook-exam --parent-tag local
python scripts/image_builder build ml-notebook-exam --parent-tag dev-sha-a10dab6

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
  `notebooks.toml`. Run `python scripts/image_builder tree` to check it. End its Dockerfile
  with the `image_info record` block (copy it from any other image).
- Tests: `pip install -r scripts/image_builder/requirements-dev.txt`, then `python -m pytest`.

## Contributing

If you'd like to contribute to this repository, please feel free to open an issue or submit a pull request.

## License

The images in this repository are licensed under MIT.
