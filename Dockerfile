FROM python:3.12

# Install Java for Spark 
RUN apt-get update && \
    apt-get install -y default-jdk && \
    apt-get clean

COPY . ./app

WORKDIR /app

# Using this example-compute-block for testing, you have to copy your current version of scystream-sdk into this
# directory. We copy it into the docker container, and install it there via the folder.
RUN python3 -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install ./scystream-sdk

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Keep the container running. Just for testing, normally placeholder which will be overriden by DockerOperator
CMD ["tail", "-f", "/dev/null"]
