from e2xgrader.config import configure_base, configure_exchange

c = get_config()  # noqa: F821
configure_base(c)
configure_exchange(c)
