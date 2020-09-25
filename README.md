# StorageLeaf

Accepts sensor data and saves them into a database. The saved data can be accessed via api.

## Installation on Raspberry Pi Zero
- pipenv is causing some problems
- use pipenv 2018-11-26
- run `pipenv lock`
- open `Pipfile.lock` and remove the `gevent` dependency
- run `Pipenv sync`
- install gevent manually via `pipenv install gevent`