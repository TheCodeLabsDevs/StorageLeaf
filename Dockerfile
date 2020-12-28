FROM python:3-buster

RUN pip install pipenv
COPY src /opt/StorageLeaf/src
COPY docs /opt/StorageLeaf/docs
COPY Pipfile /opt/StorageLeaf

WORKDIR /opt/StorageLeaf
RUN pipenv install
RUN ln -s $(pipenv --venv) /opt/StorageLeaf/mypipenv

WORKDIR /opt/StorageLeaf/src
CMD [ "/opt/StorageLeaf/mypipenv/bin/python", "/opt/StorageLeaf/src/StorageLeaf.py" ]
