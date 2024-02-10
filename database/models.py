# models.py
from sqlalchemy import Float, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Stock(Base):
    __tablename__ = "gpw_stocks_list"
    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    name = Column(String)


class CashFlowStatement(Base):
    __tablename__ = "cash_flow_statement"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    CompanyName = Column(String)
    PublicationDate = Column(String)
    OperatingCashFlows = Column(String, nullable=True)
    Depreciation = Column(String, nullable=True)
    InvestingCashFlows = Column(String, nullable=True)
    CapitalExpenditures = Column(String, nullable=True)
    FinancingCashFlows = Column(String, nullable=True)
    StockIssuance = Column(String, nullable=True)
    DividendsPaid = Column(String, nullable=True)
    StockRepurchase = Column(String, nullable=True)
    LeasePayments = Column(String, nullable=True)
    TotalCashFlows = Column(String, nullable=True)
    FreeCashFlow = Column(String, nullable=True)


class TestTable(Base):
    __tablename__ = "test_table1"
    id = Column(
        Integer, primary_key=True, autoincrement=True
    )  # Adding an ID column as a primary key
    PublicationDate = Column(String)
    OperatingCashFlows = Column(String)


engine = create_engine("sqlite:///database/stocks.db")
Base.metadata.create_all(engine)
