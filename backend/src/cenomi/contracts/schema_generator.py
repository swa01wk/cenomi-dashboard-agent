"""JSON Schema export constrained to the ADR-0004 subset."""

from __future__ import annotations

from typing import Any

from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue


class CenomiGenerateJsonSchema(GenerateJsonSchema):
    """Export schemas without forbidden keywords (defaults, discriminator, anyOf, allOf)."""

    def nullable_schema(self, schema: Any) -> JsonSchemaValue:
        # Optional fields are absent on the wire, not null (ADR-0004 §4 g).
        return self.generate_inner(schema["schema"])

    def tagged_union_schema(self, schema: Any) -> JsonSchemaValue:
        result = super().tagged_union_schema(schema)
        result.pop("discriminator", None)
        if "oneOf" not in result and "anyOf" in result:
            result["oneOf"] = result.pop("anyOf")
        return result

    def union_schema(self, schema: Any) -> JsonSchemaValue:
        one_of: list[JsonSchemaValue] = []
        for choice in schema["choices"]:
            one_of.append(self.generate_inner(choice))
        return {"oneOf": one_of}

    def default_schema(self, schema: Any) -> JsonSchemaValue:
        inner = schema.get("schema", schema)
        return self.generate_inner(inner)
