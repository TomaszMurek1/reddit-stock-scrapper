# models.py
from sqlalchemy import Float, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Stock(Base):
    __tablename__ = "gpw_stocks_list"
    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    name = Column(String)
    market = Column(String)


class GpwCashFlowStatement(Base):
    __tablename__ = "gpw_cash_flow_statement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String)
    publication_date = Column(String)
    operating_cash_flows = Column(String, nullable=True)
    depreciation = Column(String, nullable=True)
    investing_cash_flows = Column(String, nullable=True)
    capital_expenditures = Column(String, nullable=True)
    financing_cash_flows = Column(String, nullable=True)
    stock_issuance = Column(String, nullable=True)
    dividends_paid = Column(String, nullable=True)
    stock_repurchase = Column(String, nullable=True)
    lease_payments = Column(String, nullable=True)
    total_cash_flows = Column(String, nullable=True)
    free_cash_flow = Column(String, nullable=True)


class GpwBalanceSheet(Base):
    __tablename__ = "gpw_balance_sheet"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String)
    sales_revenue = Column(Float, nullable=True)
    cost_of_goods_sold = Column(Float, nullable=True)
    selling_expenses = Column(Float, nullable=True)
    general_administrative_expenses = Column(Float, nullable=True)
    gross_profit = Column(Float, nullable=True)
    other_operating_income = Column(Float, nullable=True)
    other_operating_expenses = Column(Float, nullable=True)
    operating_income_ebit = Column(Float, nullable=True)
    financial_income = Column(Float, nullable=True)
    financial_expenses = Column(Float, nullable=True)
    other_income_expense = Column(Float, nullable=True)
    operating_profit = Column(Float, nullable=True)
    extraordinary_items = Column(Float, nullable=True)
    pre_tax_income = Column(Float, nullable=True)
    net_income_from_discontinued_operations = Column(Float, nullable=True)
    net_income = Column(Float, nullable=True)
    net_income_to_majority_shareholders = Column(Float, nullable=True)
    ebitda = Column(Float, nullable=True)


engine = create_engine("sqlite:///database/stocks.db")
Base.metadata.create_all(engine)
