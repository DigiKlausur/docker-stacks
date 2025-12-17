"""
nbgrader configuration file.

This uses the environment variables:
- LANGUAGE: The language to use (default: en)

- NBGRADER_TIMEZONE: The timezone to use (default: Europe/Berlin)

- NBGRADER_COURSE_DIR: The root directory for the course (default: ~/course)
- NBGRADER_COURSE_ID: The course id (default: course101)
- NBGRADER_GROUPSHARED: Whether the course directory is group-shared (default: true)

- NBGRADER_EXCHANGE_DIR: The exchange directory (default: /srv/nbgrader/exchange)
- NBGRADER_EXCHANGE_PERSONALIZED_INBOUND: Whether to use personalized inbound exchange
- NBGRADER_EXCHANGE_PERSONALIZED_OUTBOUND: Whether to use personalized outbound exchange
- NBGRADER_EXCHANGE_PERSONALIZED_FEEDBACK: Whether to use personalized feedback exchange

- NBGRADER_EXECUTE_TIMEOUT: The timeout for executing notebooks in seconds (default: 300)

- E2X_DRAWIO_DOMAIN: The domain to use for the diagram editor (default: None)
- E2X_DRAWIO_ORIGIN: The origin to use for the diagram editor (default: None)
"""
import os

from e2xgrader.config import configure_base, configure_exchange

c = get_config()  # noqa: F821
configure_base(c)
configure_exchange(c)

# Fix permissions for exchange directory
c.BaseConverter.permissions = 444      # r--r--r--
c.GenerateAssignment.permissions = 664 # rw-rw-r--
c.GenerateFeedback.permissions = 664   # rw-rw-r--
c.GenerateSolution.permissions = 664   # rw-rw-r--

c.CourseDirectory.ignore = [
    ".ipynb_checkpoints",
    "__pycache__",
    "*.pyc",
    "feedback",
    ".*"
]

# ------------------------ #
#  Timezone                #
# ------------------------ #
c.NbGraderAPI.timezone = os.getenv("NBGRADER_TIMEZONE", "Europe/Berlin")
c.Exchange.timezone = os.getenv("NBGRADER_TIMEZONE", "Europe/Berlin")

# ------------------------ #
# Course Directory         #
# ------------------------ #
course_dir = os.getenv("NBGRADER_COURSE_DIR")
if course_dir:
    c.CourseDirectory.root = os.path.expanduser(course_dir)
c.CourseDirectory.course_id = os.getenv("NBGRADER_COURSE_ID", "course101")
c.CourseDirectory.groupshared = os.getenv("NBGRADER_GROUPSHARED", "true").lower() in ("true")

# ------------------------ #
# Exchange                 #
# ------------------------ #
c.Exchange.root = os.getenv("NBGRADER_EXCHANGE_DIR", "/srv/nbgrader/exchange")
exchange_personalized_inbound = os.getenv("NBGRADER_EXCHANGE_PERSONALIZED_INBOUND")
if exchange_personalized_inbound:
    c.Exchange.personalized_inbound = exchange_personalized_inbound.lower() in ("true")
exchange_personalized_outbound = os.getenv("NBGRADER_EXCHANGE_PERSONALIZED_OUTBOUND")
if exchange_personalized_outbound:
    c.Exchange.personalized_outbound = exchange_personalized_outbound.lower() in ("true")
exchange_personalized_feedback = os.getenv("NBGRADER_EXCHANGE_PERSONALIZED_FEEDBACK")
if exchange_personalized_feedback:
    c.Exchange.personalized_feedback = exchange_personalized_feedback.lower() in ("true")

if os.getenv("LANGUAGE", "en") == "de":
    c.SubmissionExporter.exam_submitted_message = "Ihre Klausur wurde erfolgreich abgegeben."
    c.SubmissionExporter.your_hashcode_message = "Ihr Hashcode lautet:"
    c.SubmissionExporter.verify_exam_message = "Bitte überprüfen Sie Ihre Klausur unten und schalten Sie den Rechner aus."

# ------------------------ #
# Diagram Editor           #
# ------------------------ #
draw_domain = os.getenv("E2X_DRAWIO_DOMAIN")
if draw_domain:
    c.DiagramEditor.drawDomain = draw_domain
draw_origin = os.getenv("E2X_DRAWIO_ORIGIN")
if draw_origin:
    c.DiagramEditor.drawOrigin = draw_origin

# ------------------------ #
# Additional Configuration #
# ------------------------ #
c.ExecutePreprocessor.timeout = int(os.getenv("NBGRADER_EXECUTE_TIMEOUT", 300))
