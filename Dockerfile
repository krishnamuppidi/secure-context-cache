FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY examples ./examples
COPY config ./config
RUN pip install --no-cache-dir -e ".[api]"

RUN useradd --create-home --uid 10001 acg
USER 10001

EXPOSE 8080
CMD ["uvicorn", "agent_context_gateway.api:app", "--host", "0.0.0.0", "--port", "8080"]
