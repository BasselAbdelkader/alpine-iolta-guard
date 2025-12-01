"""
ASGI config for trust_account_project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trust_account_project.settings')

application = get_asgi_application()