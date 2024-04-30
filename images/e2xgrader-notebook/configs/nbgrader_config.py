from e2xgrader.config import configure_base, configure_exchange

c = get_config()  # noqa: F821
configure_base(c)
configure_exchange(c)

# Fix permissions for exchange directory
c.BaseConverter.permissions = 444      # r--r--r--
c.GenerateAssignment.permissions = 664 # rw-rw-r--
c.GenerateFeedback.permissions = 664   # rw-rw-r--
c.GenerateSolution.permissions = 664   # rw-rw-r--
