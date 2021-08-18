import os

from sqlalchemy.orm import Session

from Settings import SETTINGS
from logic.database import Schemas, Crud


def get_database_info(db: Session) -> Schemas.DatabaseInfo:
    numberOfMeasurements = Crud.get_total_number_of_measurements(db)

    sizeInBytes = os.path.getsize(SETTINGS['database']['databasePath'])
    sizeInMegaBytes = sizeInBytes // 1024 // 1024

    return Schemas.DatabaseInfo(number_of_measurements=numberOfMeasurements,
                                size_on_disk_in_mb=sizeInMegaBytes)