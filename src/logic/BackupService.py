import logging

from TheCodeLabs_BaseUtils.OwncloudUploader import OwncloudUploader

from logic import Constants

LOGGER = logging.getLogger(Constants.APP_NAME)


class BackupService:
    def __init__(self,
                 fileToBackup: str,
                 enable: bool,
                 maxModifications: int,
                 owncloudHost: str,
                 owncloudUser: str,
                 owncloudPassword: str,
                 owncloudDestinationPath: str):
        self._fileToBackup = fileToBackup
        self._enable = enable
        self._maxModifications = maxModifications
        self._owncloudHost = owncloudHost
        self._owncloudUser = owncloudUser
        self._owncloudPassword = owncloudPassword
        self._owncloudDestinationPath = owncloudDestinationPath

        self.__reset()

    def __reset(self):
        self._numberOfModifications = 0

    def is_backup_needed(self):
        if not self._enable:
            return False

        return self._numberOfModifications >= self._maxModifications

    def backup(self):
        try:
            LOGGER.info('Running backup...')
            uploader = OwncloudUploader(self._owncloudHost, self._owncloudUser, self._owncloudPassword)
            uploader.upload(self._owncloudDestinationPath, self._fileToBackup)
            self.__reset()
        except Exception:
            LOGGER.exception('Error performing backup')

    def perform_modification(self):
        self._numberOfModifications += 1
        LOGGER.debug(f'New Modification ({self._numberOfModifications}/{self._maxModifications})')
        if self.is_backup_needed():
            self.backup()
