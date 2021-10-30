# StorageLeaf

Accepts sensor data and saves them into a database. The saved data can be accessed via api.  
An interactive OpenAPI Swagger documentation can be accessed by opening the server url in your web browser (e.g. http://localhost:10003).

## Commonly used sensor types
- temperature
- humidity

## Automatic database cleanup
Collecting data from many sensors in short time intervals will eventually lead to an increased database size.  
The total number of measurements and the size on disk can be retrieved via the API: GET [http://localhost:10003/database/databaseInfo](http://localhost:10003/database/databaseInfo)

StorageLeaf provides an automatic cleanup procedure that deletes old measurements based on retention policies.``

### Settings
All cleanup settings are specified in the database section in `settings.json`.
```json
"cleanup": {
    "forceBackupAfterCleanup": false,
    "retentionPolicies": [
        {
            "numberOfMeasurementsPerDay": 24,
            "ageInDays": 30
        }
    ],
    "retentionPolicies": {
        "enable": true,
        "cronSchedule": "* * * * *"
    }
}
```

- `forceBackupAfterCleanup` - If true, a backup is enforced after cleanup (instead of waiting for configured number of modifications).
- `automatic` - The cleanup process can run automatically.
  - `enable` - Enables the scheduling of automatic cleanup.
  - `cronSchedule` - Specifies the schedule for the automatic cleanup in cron syntax. (Note: If a cleanup is still running when the next cron trigger fires, the running cleanup is not aborted and the trigger discarded.)
- `retentionPolicies` - Specifies how the measurements are cleaned.
  - `ageInDays` - All measurements older than this number of days will be affected by this retention policy. 
  - `numberOfMeasurementsPerDay` - While running the cleanup process all measurements are grouped by date. Each retention policy specifies how many measurements are kept at most for every day. To determine which measurements should be kept, the date is divided into equally spaced time points. For every time point the closest measurement will be kept.   


**Note:** The initial cleanup of an existing database can take a considerable amount of time to complete!

The cleanup can also be triggered manually via API: POST [http://localhost:10003/database/databaseCleanup](http://localhost:10003/database/databaseCleanup)  
The status is available via GET [http://localhost:10003/database/databaseCleanup](http://localhost:10003/database/databaseCleanup)

## Credits

### Icons
- leaf icon - made by Freepik from [https://www.flaticon.com/](https://www.flaticon.com/)]
- database solid icon - made by Pixel perfect from [https://www.flaticon.com/](https://www.flaticon.com/)]

### Python libraries
See `Pipfile` and `Pipfile.lock`
(This project uses some personal libraries not available on the official pypi. The source code can be found here [https://thecodelabs.de/TheCodeLabs/PythonLibs](https://thecodelabs.de/TheCodeLabs/PythonLibs))
