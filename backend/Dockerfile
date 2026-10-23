# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

RUN groupadd --system cenomi && useradd --system --gid cenomi --create-home cenomi

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv

WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock /app/backend/
RUN uv sync --locked --directory /app/backend --no-dev --no-install-project

COPY backend/src /app/backend/src
COPY specs /app/specs
RUN uv sync --locked --directory /app/backend --no-dev

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/backend/.venv/bin:${PATH}"

USER cenomi
WORKDIR /app/backend
EXPOSE 8000

CMD ["uvicorn", "cenomi.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
