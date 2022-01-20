from ..shared.db_manager import Base, engine


def init_db():
    from .models.schedule import Schedule
    Base.metadata.create_all(bind=engine)

