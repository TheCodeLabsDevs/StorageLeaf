FROM python:3.9-alpine

RUN apk add --no-cache openssl-dev libffi-dev gcc musl-dev make

RUN pip install pipenv
COPY src /opt/StorageLeaf/src
COPY docs /opt/StorageLeaf/docs
COPY Pipfile /opt/StorageLeaf

WORKDIR /opt/StorageLeaf
RUN pipenv install
RUN ln -s $(pipenv --venv) /opt/StorageLeaf/mypipenv

WORKDIR /opt/StorageLeaf/src
CMD [ "/opt/StorageLeaf/mypipenv/bin/python", "/opt/StorageLeaf/src/StorageLeaf.py" ]
