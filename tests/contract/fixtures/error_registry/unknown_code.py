from cenomi.core.errors import CenomiError


class UnknownCode(CenomiError):
    def __init__(self) -> None:
        super().__init__(code="NOT_A_REAL_CODE", message="x", retryable=False, http_status=500)
