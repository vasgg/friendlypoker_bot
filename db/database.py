from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import db_string
from db.models import Base

engine = create_engine(db_string, echo=True)
Session = sessionmaker(engine, expire_on_commit=False)
session = Session()

with session.begin():
    Base.metadata.create_all(engine)
