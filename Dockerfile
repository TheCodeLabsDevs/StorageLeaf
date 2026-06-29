FROM python:3.14-slim AS poetry

RUN apt-get update && apt-get install -y \
    curl gcc python3-dev libc-dev build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://install.python-poetry.org | python -

COPY pyproject.toml /opt/StorageLeaf/pyproject.toml
COPY poetry.lock /opt/StorageLeaf/poetry.lock
COPY src/ /opt/StorageLeaf/src

WORKDIR /opt/StorageLeaf
RUN /root/.local/bin/poetry install --no-root
RUN ln -s $($HOME/.local/share/pypoetry/venv/bin/poetry env info -p) /opt/StorageLeaf/venv

FROM python:3.14-slim

RUN apt-get update && apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

COPY src/ /opt/StorageLeaf/src
COPY --from=poetry /opt/StorageLeaf/venv /opt/StorageLeaf/venv

RUN adduser StorageLeaf && chown -R StorageLeaf:StorageLeaf /opt/StorageLeaf
USER StorageLeaf

WORKDIR /opt/StorageLeaf/src
EXPOSE 10003
CMD [ "/opt/StorageLeaf/venv/bin/python", "/opt/StorageLeaf/src/StorageLeaf.py"]
