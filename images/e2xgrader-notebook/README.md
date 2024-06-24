# E2xGrader Notebook

This Docker image is used to install `e2xgrader` and activate a specific mode.   
More information on e2xgrader can be found [here](https://github.com/Digiklausur/e2xgrader).

## Build Args

The following build arg is available:

* `IMAGE_SOURCE`: The base image to use for the build. Defaults to `jupyter/minimal-notebook:notebook-6.5.4`.
* `E2XGRADER_MODE`: The specific e2xgrader mode to activate. Can be one of `student`, `teacher` or `student_exam`. Defaults to `student`.
* `E2XGRADER_VERSION`: The specific e2xgrader version to install from PyPI. If not set defaults to the latest version. Does take no effect if `FROM_REPO` is `true`.
* `FROM_REPO`: If e2xgrader should be installed from the [GitHub repository](https://github.com/Digiklausur/e2xgrader). Defaults to `false`.
* `E2XGRADER_BRANCH`: Specifies the branch to install from if `FROM_REPO` is `true`. Defaults to `main`.

## Description

This image is designed to build e2xgrader end-point images for the other images in this repository.

* It first installs common requirements for all modes, including:
    + An `nbgrader_config.py` activating `e2xgrader` preprocessors and the `e2xgrader` exchange
    + [e2xgradingtools](https://github.com/DigiKlausur/e2xgradingtools) for testing students code
    + [exam_kernel](https://github.com/DigiKlausur/exam_kernel) for providing a restricted and configurable Python kernel
    + [java_syntax_kernel](https://github.com/DigiKlausur/java_syntax_kernel) for providing a simple kernel that highlights JAVA code without executing it.

### Teacher mode

If `E2XGRADER_MODE` is set to `teacher` it will:

* Install wkhtml2pdf and [pdf_feedback_exporter](https://github.com/DigiKlausur/e2xgradingtools) for generating PDF versions of student feedback files
* Install RISE for Jupyter Notebook slide shows
* Install [e2x_exam_sheets](https://github.com/DigiKlausur/e2xgradingtools) for generating seating cards and login sheets for exams.

### Student mode

If `E2XGRADER_MODE` is set to `student` it will:

* Install RISE for Jupyter Notebook slide shows
* Activate student extensions 

### Student Exam mode

If `E2XGRADER_MODE` is set to `student_exam` it will:

* Activate student exam extensions, providing a restricted notebook environment.
* Activate a custom submit toolbar in notebooks
* Activate custom submit behavior that hashes student files on submission and provides HTML versions of all submitted notebooks

## Usage

### Pull and Run

Instead of pulling and running this image directly, refer to the e2xgrader versions of the other images present in this repository.

### Build and Run

To create a teacher version of a specific notebook run:

```
docker build -t your-notebook-teacher:dev \
       --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>" \
       --build-arg="E2XGRADER_MODE=teacher"
```

To create a student version of a specific notebook run and install `e2xgrader` from the `dev` branch run:

```
docker build -t your-notebook-student:dev \
       --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>" \       
       --build-arg="E2XGRADER_MODE=student" \
       --build-arg="FROM_REPO=true" \
       --build-arg="E2XGRADER_BRANCH=dev"
```