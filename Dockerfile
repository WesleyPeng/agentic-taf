FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/WesleyPeng/agentic-taf"
LABEL org.opencontainers.image.description="Agentic-TAF test runner"
LABEL org.opencontainers.image.licenses="LGPL-3.0"

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl openssh-client && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers
RUN pip install --no-cache-dir playwright && playwright install --with-deps chromium

# Install framework dependencies
COPY src/main/python/requirements.txt /app/requirements.txt
COPY src/main/python/requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r /app/requirements-dev.txt

# Install optional deps for all test types
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md
COPY src /app/src
WORKDIR /app
RUN pip install --no-cache-dir -e ".[all,dev]" 2>/dev/null || pip install --no-cache-dir -e ".[dev]"

ENV PYTHONPATH=/app/src/main/python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["pytest"]
CMD ["src/test/python/ut/", "-v", "--junitxml=reports/unit-tests.xml"]
