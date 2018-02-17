import logging
from .user import post_pritunl_user
from .user import delete_pritunl_user
from .auth import pritunl_auth_request

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
