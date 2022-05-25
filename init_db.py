from tools import db


def init_db():
    from .models.schedule import Schedule
    db.Base.metadata.create_all(bind=db.engine)

