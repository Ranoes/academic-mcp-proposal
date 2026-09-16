FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr (crucial for MCP stdio communication)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt pyproject.toml README.md ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY canvas_validator.py builder_engine.py praproposal_builder.py server.py csv_ingestor.py topic_synthesizer.py diagram_generator.py ./
COPY assets/ /app/assets/


# Install the academic proposal package
RUN pip install --no-cache-dir -e .

# Workspace directory for mounting host files
ENV WORKSPACE_DIR=/workspace
VOLUME /workspace
WORKDIR /workspace

ENTRYPOINT ["python", "/app/server.py"]

