"""ASGI entrypoint (ARCH-R008)."""

from cenomi.api.app import create_app
from cenomi.api.health_wiring import bind_db_health_check
from cenomi.db.health import check_database

bind_db_health_check(check_database)

app = create_app()
