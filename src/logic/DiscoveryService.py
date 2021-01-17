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
        LOGGER.debug(f'Start discovery thread (listening on {self._discoveryPort}, responding on {self._responsePort})')

        x = threading.Thread(target=self.__loop)
        x.start()

    def __loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('', self._discoveryPort))

            while not self._shouldStop:
                try:
                    data, remoteIpAndPort = sock.recvfrom(1024)
                    data = data.strip()
                    remoteIp, __port = remoteIpAndPort

                    if data.decode() == self._requestMessage:
                        LOGGER.debug(f'Received discovery request from {remoteIp}')
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as responseSock:
                            responseSock.connect((remoteIp, self._responsePort))
                            response = f'{self._responseMessage};{self._apiPort}'
                            responseSock.sendall(response.encode())
                except BaseException as e:
                    LOGGER.error(e)

    def stop(self):
        self._shouldStop = True
