from datetime import datetime
from typing import Dict

from sqlalchemy.orm import Session

from logic.database import Schemas, DatabaseInfoProvider
from logic.database.DatabaseCleaner import DatabaseCleaner
from logic.database.RetentionPolicy import RetentionPolicy


class DatabaseCleanupService:
    def __init__(self, cleanupSettings: Dict):
        self._cleanupSettings = cleanupSettings

    def cleanup(self, db: Session) -> Schemas.DatabaseCleanupInfo:
        infoBefore = DatabaseInfoProvider.get_database_info(db)

        retentionPolicies = self._cleanupSettings['retentionPolicies']
        policies = []
        for item in retentionPolicies:
            policies.append(RetentionPolicy(numberOfMeasurementsPerDay=item['numberOfMeasurementsPerDay'],
                                            ageInDays=item['ageInDays']))

        DatabaseCleaner(policies, self._cleanupSettings['forceBackupAfterCleanup']).clean(db, datetime.now().date())

        infoAfter = DatabaseInfoProvider.get_database_info(db)

        deletedMeasurements = infoBefore.number_of_measurements - infoAfter.number_of_measurements
        sizeFreed = infoBefore.size_on_disk_in_mb - infoAfter.size_on_disk_in_mb
        infoDifference = Schemas.DatabaseInfo(number_of_measurements=deletedMeasurements, size_on_disk_in_mb=sizeFreed)

        return Schemas.DatabaseCleanupInfo(status=Schemas.DatabaseCleanupStatus.FINISHED, before=infoBefore,
                                           after=infoAfter, difference=infoDifference)
