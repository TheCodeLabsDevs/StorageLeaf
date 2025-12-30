FROM python:3.13-alpine AS poetry

RUN apk update && apk upgrade && \
    apk add curl gcc python3-dev libc-dev build-base linux-headers && \
    rm -rf /var/cache/apk
RUN curl https://install.python-poetry.org | python -

COPY pyproject.toml /opt/StorageLeaf/pyproject.toml
COPY poetry.lock /opt/StorageLeaf/poetry.lock
COPY src/ /opt/StorageLeaf/src

WORKDIR /opt/StorageLeaf
RUN /root/.local/bin/poetry install --no-root
RUN ln -s $($HOME/.local/share/pypoetry/venv/bin/poetry env info -p) /opt/StorageLeaf/venv

FROM python:3.13-alpine

RUN apk update && apk upgrade && \
    rm -rf /var/cache/apk

COPY src/ /opt/StorageLeaf/src
COPY --from=poetry /opt/StorageLeaf/venv /opt/StorageLeaf/venv

RUN adduser -D StorageLeaf && chown -R StorageLeaf:StorageLeaf /opt/StorageLeaf
USER StorageLeaf

WORKDIR /opt/StorageLeaf/src
EXPOSE 10003
CMD [ "/opt/StorageLeaf/venv/bin/python", "/opt/StorageLeaf/src/StorageLeaf.py"]
