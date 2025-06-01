# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if any were found to be necessary (none identified so far for vision-parse core)
# RUN apt-get update && apt-get install -y ...

# Upgrade pip
RUN pip install --upgrade pip

# Copy packaging configuration files
COPY pyproject.toml ./
# COPY hatch.toml ./ # If hatch.toml is used by the build system and is present

# Install dependencies
# Using .[all] to ensure all extras like openai, gemini are included
RUN pip install .[all]

# Copy the rest of the application source code
COPY src/ ./src/
# COPY run_vision_parse.py ./ # This file will be created in a later step,
                              # alternatively, a broader COPY . . can be used here or after this.
                              # For now, just ensure src is copied.

# The docker-compose.yml uses `tail -f /dev/null` as the command to keep the container running.
# So, no specific CMD or ENTRYPOINT is strictly needed in this Dockerfile if used with that docker-compose.yml.
