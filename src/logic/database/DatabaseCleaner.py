import logging
from dataclasses import dataclass
from typing import List

from sqlalchemy.orm import Session

from logic import Constants

LOGGER = logging.getLogger(Constants.APP_NAME)


@dataclass
class RetentionPolicy:
    resolutionInMinutes: int
    ageInDays: int


class DatabaseCleaner:
    def __init__(self, retentionPolicies: List[RetentionPolicy]):
        self._policies = retentionPolicies

    def clean(self, db: Session):
        LOGGER.info('Performing database cleanup...')

        for policy in self._policies:
            LOGGER.debug(f'Enforcing retention policy: {policy}')

        LOGGER.info('Database cleanup done')
