from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from Settings import SETTINGS

databasePath = SETTINGS['database']['databasePath']
databaseUrl = f'sqlite:///{databasePath}'

engine = create_engine(
    databaseUrl, connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
