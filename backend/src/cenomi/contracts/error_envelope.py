"""error_envelope.v1 — non-2xx API response body."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

_MODEL = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    extra="forbid",
)


class ErrorDetail(BaseModel):
    model_config = _MODEL

    path: str = Field(
        max_length=200,
        description="Location of the problem, for example body.principalId or query.limit.",
    )
    rule: str = Field(
        pattern=r"^[a-z][a-z0-9_]{1,63}$",
        description="Violated rule, for example required, unknown_field, max_value.",
    )


class ErrorBody(BaseModel):
    model_config = _MODEL

    code: str = Field(
        pattern=r"^[A-Z][A-Z0-9_]{2,63}$",
        description=(
            "Registry code (error_codes.v1.yaml). The pattern, not an enum, constrains it "
            "so later milestones can add codes additively."
        ),
    )
    message: str = Field(min_length=1, max_length=500)
    request_ref: str = Field(
        pattern=r"^req_[0-9a-f]{16}$",
        description=(
            "Server-assigned reference of the HTTP request (ARCH-R020); also sent in "
            "the X-Request-Ref header."
        ),
    )
    retryable: bool = Field(
        description=(
            "True when retrying the same request may succeed (for example DEPENDENCY_UNAVAILABLE)."
        )
    )
    details: list[ErrorDetail] | None = Field(
        default=None,
        max_length=50,
        description=(
            "Optional structured detail, used by VALIDATION_ERROR. Never echoes submitted values."
        ),
        json_schema_extra={"maxItems": 50},
    )


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        json_schema_extra={
            "title": "ErrorEnvelope v1",
            "description": (
                "Body of every non-2xx API response (ARCH-R015). Codes come from "
                "specs/contracts/error_codes.v1.yaml. Messages are plain language and never "
                "contain SQL, stack traces, secrets, submitted values or names of out-of-scope "
                "entities (ARCH-R025). Bootstrap contract (ADR-0004 §1), frozen by CF-0."
            ),
            "examples": [
                {
                    "error": {
                        "code": "NOT_AVAILABLE",
                        "message": "This isn't available.",
                        "requestRef": "req_8f21c4a09b7e3d15",
                        "retryable": False,
                    }
                },
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "The request is not valid.",
                        "requestRef": "req_00a1b2c3d4e5f607",
                        "retryable": False,
                        "details": [{"path": "query.region", "rule": "unknown_field"}],
                    }
                },
                {
                    "error": {
                        "code": "DEPENDENCY_UNAVAILABLE",
                        "message": "The service is temporarily unavailable. Try again.",
                        "requestRef": "req_1234567890abcdef",
                        "retryable": True,
                    }
                },
            ],
        },
    )

    error: ErrorBody
