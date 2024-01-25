from sqlalchemy.orm import sessionmaker
from .models import engine

Session = sessionmaker(bind=engine)


def get_session():
    return Session()
