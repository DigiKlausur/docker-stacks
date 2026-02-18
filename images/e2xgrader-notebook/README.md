# E2xGrader Notebook

This Docker image is used to install `e2xgrader` and activate a specific mode.   
More information on e2xgrader can be found [here](https://github.com/Digiklausur/e2xgrader).

## Build Args

The following build args are available:

* `IMAGE_SOURCE`: The base image to use for the build. Defaults to `ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest`.
* `E2XGRADER_VERSION`: The specific e2xgrader version to install from PyPI. If not set defaults to the latest version. Does take no effect if `FROM_REPO` is `true`.
* `FROM_REPO`: If e2xgrader should be installed from the [GitHub repository](https://github.com/Digiklausur/e2xgrader). Defaults to `false`.
* `E2XGRADER_BRANCH`: Specifies the branch to install from if `FROM_REPO` is `true`. Defaults to `main`.

## Build Targets

This image uses multistage builds with the following available targets:

* `base`: Base configuration with common requirements for all modes
* `student`: Student mode configuration
* `student_exam`: Student exam mode configuration with restricted environment
* `teacher`: Teacher mode configuration with grading and assignment management tools

## Description

This image is designed to build e2xgrader end-point images for the other images in this repository using multistage builds.

The `base` target installs common requirements for all modes, including:
* An `nbgrader_config.py` activating `e2xgrader` preprocessors and the `e2xgrader` exchange
* [e2xgradingtools](https://github.com/DigiKlausur/e2xgradingtools) for testing students code
* [exam_kernel](https://github.com/DigiKlausur/exam_kernel) for providing a restricted and configurable Python kernel
* [java_syntax_kernel](https://github.com/DigiKlausur/java_syntax_kernel) for providing a simple kernel that highlights JAVA code without executing it.

### Environment Variables

These images can be customized using environment variables. For all modes the following environment variables are present.

* `LANGUAGE`: The language to use (default: en). This currently only affects the submission html generated in `student_exam` mode.

* `NBGRADER_TIMEZONE`: The timezone to use (default: Europe/Berlin)

* `NBGRADER_COURSE_DIR`: The root directory for the course (default: ~/course)
* `NBGRADER_COURSE_ID`: The course id (default: course101)
* `NBGRADER_GROUPSHARED`: Whether the course directory is group-shared (default: true)

* `NBGRADER_EXCHANGE_DIR`: The exchange directory (default: /srv/nbgrader/exchange)
* `NBGRADER_EXCHANGE_PERSONALIZED_INBOUND`: Whether to use personalized inbound exchange. If active students submit to their own directory.
* `NBGRADER_EXCHANGE_PERSONALIZED_OUTBOUND`: Whether to use personalized outbound exchange. If active students fetch from their own directory. This can be used to provide each student with a personalized assignment.
* `NBGRADER_EXCHANGE_PERSONALIZED_FEEDBACK`: Whether to use personalized feedback exchange. If active students fetch feedback from their own directory.

* `NBGRADER_EXECUTE_TIMEOUT`: The timeout for executing notebooks in seconds (default: 300)

* `E2X_DRAWIO_DOMAIN`: The domain to use for the diagram editor (default: None). If None is set then `https://embed.diagrams.net/` is used.
* `E2X_DRAWIO_ORIGIN`: The origin to use for the diagram editor (default: None). If None is set then `https://embed.diagrams.net/` is used.

### Teacher Target

The `teacher` target builds from the `base` stage and:

* Installs wkhtml2pdf and [pdf_feedback_exporter](https://github.com/DigiKlausur/e2xgradingtools) for generating PDF versions of student feedback files
* Installs RISE for Jupyter Notebook slide shows
* Installs [e2x_exam_sheets](https://github.com/DigiKlausur/e2xgradingtools) for generating seating cards and login sheets for exams
* Activates e2xgrader in teacher mode

### Student Target

The `student` target builds from the `base` stage and:

* Installs RISE for Jupyter Notebook slide shows
* Activates e2xgrader in student mode with student extensions

### Student Exam Target

The `student_exam` target builds from the `base` stage and:

* Activates student exam extensions, providing a restricted notebook environment
* Activates a custom submit toolbar in notebooks
* Activates custom submit behavior that hashes student files on submission and provides HTML versions of all submitted notebooks
* Activates e2xgrader in student_exam mode

In student exam mode the following additional environment variables can be used to configure automated backups using [E2X Jupyter Backup](https://github.com/DigiKlausur/e2x-jupyter-backup).

* `E2X_BACKUP_ENABLED`: Whether the backup functionality is enabled (default: false)
* `E2X_BACKUP_DIR`: The directory where backups are stored relative to the notebook (default: None)
* `E2X_BACKUP_MAX_FILES`: The maximum number of backup files to keep per notebook (default: 10)

## Usage

### Pull and Run

Instead of pulling and running this image directly, refer to the e2xgrader versions of the other images present in this repository.

### Build and Run

To create a teacher version of a specific notebook run:

```
docker build -t your-notebook-teacher:dev \
       --target teacher \
       --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>" .
```

To create a student version of a specific notebook and install `e2xgrader` from the `dev` branch run:

```
docker build -t your-notebook-student:dev \
       --target student \
       --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>" \
       --build-arg="FROM_REPO=true" \
       --build-arg="E2XGRADER_BRANCH=dev" .
```

To create a student exam version run:

```
docker build -t your-notebook-student-exam:dev \
       --target student_exam \
       --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>" .
```

### Running the Images

After building an image, you can run it with customized environment variables. Here are some examples:

**Basic run with default settings:**

```bash
docker run -p 8888:8888 your-notebook-student:dev
```

**Run with custom course configuration:**

```bash
docker run -p 8888:8888 \
  -e NBGRADER_COURSE_ID="intro_to_python" \
  -e NBGRADER_TIMEZONE="America/New_York" \
  -v /path/to/exchange:/srv/nbgrader/exchange \
  your-notebook-teacher:dev
```

**Run student exam mode with backup enabled:**

```bash
docker run -p 8888:8888 \
  -e NBGRADER_COURSE_ID="midterm_exam" \
  -e E2X_BACKUP_ENABLED="true" \
  -e E2X_BACKUP_MAX_FILES="20" \
  -v /path/to/exchange:/srv/nbgrader/exchange \
  your-notebook-student-exam:dev
```
