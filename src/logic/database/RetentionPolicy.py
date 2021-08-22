from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List


@dataclass
class RetentionPolicy:
    numberOfMeasurementsPerDay: int
    ageInDays: int

    def determine_measurement_points(self, date: datetime.date) -> List[datetime]:
        if self.numberOfMeasurementsPerDay % 2 != 0:
            raise ValueError('"numberOfMeasurementsPerDay" must be an even number!')

        if self.numberOfMeasurementsPerDay <= 0:
            raise ValueError('"numberOfMeasurementsPerDay" must be larger than zero!')

        startTime = datetime(year=date.year, month=date.month, day=date.day, hour=0, minute=0, second=0)

        stepSizeInMinutes = 24 * 60 // self.numberOfMeasurementsPerDay

        points = []
        for index in range(self.numberOfMeasurementsPerDay):
            points.append(startTime + timedelta(minutes=stepSizeInMinutes * index))

        return points
