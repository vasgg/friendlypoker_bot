from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base
from config import db_string

engine = create_engine(db_string, echo=True)
Session = sessionmaker(engine)
session = Session()


with session.begin():
    Base.metadata.create_all(engine)
