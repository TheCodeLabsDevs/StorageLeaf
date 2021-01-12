import json

import uvicorn
from fastapi import FastAPI

from logic.databaseNew import Models
from logic.databaseNew.Database import engine
from routers import DeviceRouter

Models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(DeviceRouter.router)

with open('../settings.json', 'r', encoding='UTF-8') as f:
    settings = json.load(f)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
