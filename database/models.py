# models.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Stock(Base):
    __tablename__ = "gpw_stocks_list"
    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    name = Column(String)
    market = Column(String)

    # Additional fields and relationships


engine = create_engine("sqlite:///database/stocks.db")
Base.metadata.create_all(engine)
