FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python -

COPY . /opt/StorageLeaf
RUN rm -f /opt/StorageLeaf/settings.json

WORKDIR /opt/StorageLeaf
RUN /root/.local/bin/poetry install --no-root && \
    /root/.local/bin/poetry cache clear --all .
RUN ln -s $($HOME/.local/share/pypoetry/venv/bin/poetry env info -p) /opt/StorageLeaf/myvenv

WORKDIR /opt/StorageLeaf/src
CMD [ "/opt/StorageLeaf/myvenv/bin/python", "/opt/StorageLeaf/src/StorageLeaf.py"]
