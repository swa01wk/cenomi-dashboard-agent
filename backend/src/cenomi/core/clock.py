"""Dataset clock — business 'now' is as_of (ARCH-R029)."""

from __future__ import annotations

from datetime import date

from cenomi.core.settings import Settings


class DatasetClock:
    def __init__(self, settings: Settings) -> None:
        self._as_of = settings.cenomi_as_of

    @property
    def as_of(self) -> date:
        return self._as_of
