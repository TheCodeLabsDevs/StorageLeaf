from logic.databaseNew.Database import SessionLocal


def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
