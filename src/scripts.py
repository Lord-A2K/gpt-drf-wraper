import os
import subprocess
import sys

from . import settings


def start():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")

    try:
        import django

        django.setup()
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    gunicorn_command = [
        "gunicorn",
        "--workers",
        f"{settings.WEBSERVER_WORKERS}",
        "--bind",
        f"0.0.0.0:{settings.WEBSERVER_PORT}",
        "src.wsgi:application",
    ]

    print(f"Running command: {' '.join(gunicorn_command)}")

    try:
        subprocess.run(gunicorn_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
