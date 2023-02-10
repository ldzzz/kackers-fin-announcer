FROM python:3.9-slim-bullseye

ARG UID
ARG GID
ARG USERNAME=devUser

# Force stdin, stdout & stderr to be totally unbuffered
ENV PYTHONUNBUFFERED 1

# Don't write .pyc files in container
ENV PYTHONDONTWRITEBYTECODE 1

# Create docker non-root user
RUN groupadd -g ${GID} devUser \
    && useradd -m -u ${UID} -g devUser devUser

# Install dependencies
RUN apt -y update \
    && apt -y upgrade \
    && apt -y --no-install-recommends install \
    wget git ca-certificates build-essential

# Pull MariaDB connector cus bullseye is apparently too old already
RUN wget https://dlm.mariadb.com/2862620/Connectors/c/connector-c-3.3.4/mariadb-connector-c-3.3.4-debian-bullseye-amd64.tar.gz -O - | tar -zxf - --strip-components=1 -C /usr

# Install requirements
COPY requirements.txt /workspace/requirements.txt
WORKDIR /workspace
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install black

# Copy code
COPY ./ /workspace

# Cleanup
RUN apt -y clean \
    && apt -y autoremove \
    && rm -rf /tmp/* \
    && rm -rf /var/lib/apt/lists/*

# Change ownership to container created user
RUN chown -R ${USERNAME} . \
    && chgrp -R ${USERNAME} .

# Switch to user
USER ${USERNAME}
RUN echo "export PATH=/home/${USERNAME}/.local/bin:${PATH}" >> ~/.bashrc

# Start shell
ENTRYPOINT [ "/bin/bash" ]