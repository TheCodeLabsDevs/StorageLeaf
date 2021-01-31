# StorageLeaf

Accepts sensor data and saves them into a database. The saved data can be accessed via api.  
An interactive OpenAPI Swagger documentation can be accessed by opening the server url in your web browser (e.g. http://localhost:10003).

## Commonly used sensor types
- temperature
- humidity

---
## Credits

### Icons
- leaf icon - made by Freepik from [https://www.flaticon.com/](https://www.flaticon.com/)]
- database solid icon - made by Pixel perfect from [https://www.flaticon.com/](https://www.flaticon.com/)]

### Python libraries
See `Pipfile.lock`  
(This project uses some personal libraries not available on the official pypi. The source code can be found here [https://thecodelabs.de/TheCodeLabs/PythonLibs](https://thecodelabs.de/TheCodeLabs/PythonLibs))

---

## Installation on Raspberry Pi Zero
Pipenv can cause some problems. Possible solution:
- use pipenv 2018-11-26
- run `pipenv lock`
- open `Pipfile.lock` and remove the `gevent` dependency
- run `Pipenv sync`
- install gevent manually via `pipenv install gevent`