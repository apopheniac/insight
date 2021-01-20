# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=1

# Copy local code to the container image.
WORKDIR /usr/src/app

# add non-root user
RUN addgroup --system user && adduser --system --no-create-home --group user
RUN chown -R user:user /usr/src/app && chmod -R 755 /usr/src/app

# Install and configure dependency manager
RUN python -m pip install --upgrade pip
RUN python -m pip install poetry
RUN poetry config virtualenvs.create false

# Add and install requirements
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev --no-root

## add entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Switch to non-root user
USER user

# Add app
COPY . /usr/src/app

# Run server
CMD ["/usr/src/app/entrypoint.sh"]
