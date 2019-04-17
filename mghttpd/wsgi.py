"""
WSGI config for mghttpd project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application


if 'runserver' not in sys.argv:
    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    project_dir_path = os.path.dirname(current_dir_path)
    sys.path.append(project_dir_path)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mghttpd.settings")
application = get_wsgi_application()

if 'runserver' not in sys.argv:
    import aiowsgi
    server = aiowsgi.create_server(application, port=8000)
    server.run()
