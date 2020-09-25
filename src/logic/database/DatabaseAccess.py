import abc
import logging
import sqlite3
from abc import ABC
from enum import Enum

from logic import Constants

LOGGER = logging.getLogger(Constants.APP_NAME)


class FetchType(Enum):
    NONE = 1
    ONE = 2
    ALL = 3


class DatabaseAccess(ABC):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def namedtuple_factory(cursor, row):
        """
        Returns sqlite rows as dicts.
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __init__(self, databasePath):
        self._databasePath = databasePath

    @abc.abstractmethod
    def create_table(self):
        pass

    def _query(self, query, *args, fetch_type=FetchType.ALL):
        connection = sqlite3.connect(self._databasePath)
        connection.row_factory = DatabaseAccess.namedtuple_factory

        with connection:
            cursor = connection.cursor()
            try:
                cursor.execute(query, args)

                if fetch_type == FetchType.ONE:
                    return cursor.fetchone()
                if fetch_type == FetchType.ALL:
                    return cursor.fetchall()
            finally:
                cursor.close()
