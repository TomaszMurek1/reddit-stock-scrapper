# models.py
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    name = Column(String)
    comment = Column(Text)
    # Additional fields and relationships

engine = create_engine('sqlite:///stocks.db')
Base.metadata.create_all(engine)
