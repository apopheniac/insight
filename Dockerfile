
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=1

# Copy local code to the container image.
WORKDIR /app


# Install production dependencies.
COPY poetry.lock pyproject.toml ./
RUN python -m pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root

COPY . ./
# Run the web service on container startup. 
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 insight.app:server
# CMD exec python insight/app.py