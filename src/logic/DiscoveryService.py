import logging
import socket
import threading

from logic import Constants

LOGGER = logging.getLogger(Constants.APP_NAME)


class DiscoveryService:
    def __init__(self, discoveryPort: int, responsePort: int, requestMessage: str, responseMessage: str, apiPort: int):
        self._discoveryPort = discoveryPort
        self._responsePort = responsePort
        self._requestMessage = requestMessage
        self._responseMessage = responseMessage
        self._apiPort = apiPort

        self._shouldStop = False

    def start(self):
        LOGGER.debug("Start discovery thread")

        x = threading.Thread(target=self.__loop)
        x.start()

    def __loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('', self._discoveryPort))

            while not self._shouldStop:
                try:
                    data, ip = sock.recvfrom(1024)
                    data = data.strip()
                    ip = ip[0]

                    if data.decode() == self._requestMessage:
                        LOGGER.debug(f'Received discovery request from {ip}')
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as responseSock:
                            responseSock.connect((ip, self._responsePort))
                            response = f'{self._responseMessage};{self._apiPort}'
                            responseSock.sendall(response.encode())
                except BaseException as e:
                    LOGGER.error(e)

    def stop(self):
        self._shouldStop = True
