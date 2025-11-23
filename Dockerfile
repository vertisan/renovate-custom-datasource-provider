# Multi-stage build for smaller image size
FROM python:3.11-slim AS builder

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-ansi --without dev

# Copy source code
COPY src ./src

# Build the package
RUN poetry build


# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install the built package
COPY --from=builder /app/dist/*.whl ./
RUN pip install --no-cache-dir *.whl && rm *.whl

# Create output directory
RUN mkdir -p /output

# Set default output directory
ENV OUTPUT_DIR=/output

# Create non-root user
RUN useradd -m -u 1000 renovate && \
    chown -R renovate:renovate /app /output

USER renovate

# Set entrypoint
ENTRYPOINT ["renovate-datasource"]

# Default command
CMD ["--help"]
