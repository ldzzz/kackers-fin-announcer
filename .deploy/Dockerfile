FROM python:3.9-slim-bullseye

ARG UID
ARG GID
ARG NAME
ARG MARIADBVER=10.9.5

# Force stdin, stdout & stderr to be totally unbuffered
ENV PYTHONUNBUFFERED 1

# Don't write .pyc files in container
ENV PYTHONDONTWRITEBYTECODE 1

# Create docker NAME
RUN groupadd -g ${GID} ${NAME} \
    && useradd -m -u ${UID} -g ${NAME} ${NAME}

# Install dependencies
RUN apt -y update \
    && apt -y upgrade \
    && apt -y --no-install-recommends install \
    wget curl git ca-certificates build-essential

# Pull MariaDB connector cus bullseye is apparently too old already
RUN wget https://downloads.mariadb.com/MariaDB/mariadb_repo_setup
RUN chmod +x mariadb_repo_setup
RUN ./mariadb_repo_setup \ --mariadb-server-version="mariadb-${MARIADBVER}"
RUN apt install -y libmariadb3 libmariadb-dev

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
RUN chown -R ${NAME} . \
    && chgrp -R ${NAME} .

# Switch to user
USER ${NAME}
RUN echo "export PATH=/home/${NAME}/.local/bin:${PATH}" >> ~/.bashrc

# Start shell
ENTRYPOINT [ "python3", "/workspace/kackers_fin_announcer/bot.py" ]