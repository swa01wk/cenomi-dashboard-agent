"""ASGI entrypoint (ARCH-R008)."""

from cenomi.api.app import create_app

app = create_app()
