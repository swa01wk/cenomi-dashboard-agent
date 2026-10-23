"""Error hierarchy mapped to error_codes.v1 (ARCH-R022–R025)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ValidationDetail:
    path: str
    rule: str


@dataclass
class CenomiError(Exception):
    code: str
    message: str
    retryable: bool = False
    details: list[ValidationDetail] = field(default_factory=list)
    http_status: int = 500

    def __str__(self) -> str:
        return self.message


class ValidationFailed(CenomiError):
    def __init__(
        self,
        message: str = "The request is not valid.",
        *,
        details: list[ValidationDetail] | None = None,
    ) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            retryable=False,
            details=details or [],
            http_status=400,
        )


class Unauthenticated(CenomiError):
    def __init__(self, message: str = "Sign in to continue.") -> None:
        super().__init__(
            code="UNAUTHENTICATED",
            message=message,
            retryable=False,
            http_status=401,
        )


class NotAvailable(CenomiError):
    def __init__(self, message: str = "This isn't available.") -> None:
        super().__init__(
            code="NOT_AVAILABLE",
            message=message,
            retryable=False,
            http_status=404,
        )


class Conflict(CenomiError):
    def __init__(self, message: str = "This request conflicts with current state.") -> None:
        super().__init__(
            code="CONFLICT",
            message=message,
            retryable=False,
            http_status=409,
        )


class DependencyUnavailable(CenomiError):
    def __init__(
        self,
        message: str = "The service is temporarily unavailable. Try again.",
    ) -> None:
        super().__init__(
            code="DEPENDENCY_UNAVAILABLE",
            message=message,
            retryable=True,
            http_status=503,
        )


class Internal(CenomiError):
    def __init__(self, message: str = "Something went wrong.") -> None:
        super().__init__(
            code="INTERNAL",
            message=message,
            retryable=False,
            http_status=500,
        )


def cenomi_error_from_code(code: str, message: str | None = None) -> CenomiError:
    mapping: dict[str, type[CenomiError]] = {
        "VALIDATION_ERROR": ValidationFailed,
        "UNAUTHENTICATED": Unauthenticated,
        "NOT_AVAILABLE": NotAvailable,
        "CONFLICT": Conflict,
        "DEPENDENCY_UNAVAILABLE": DependencyUnavailable,
        "INTERNAL": Internal,
    }
    cls = mapping.get(code, Internal)
    if cls is Internal and code != "INTERNAL":
        return Internal(message or "Something went wrong.")
    return cls(message=message) if message else cls()  # type: ignore[call-arg]
