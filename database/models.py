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


class GpwProfitAndLossStatement(Base):
    __tablename__ = "gpw_profit_and_loss_statement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String)
    publication_date = Column(String)
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


class GpwBalanceSheet(Base):
    __tablename__ = "gpw_balance_sheet"

    id = Column(Integer, primary_key=True, autoincrement=True)
    publication_date = Column(String)
    company_name = Column(String)
    fixed_assets = Column(Float, nullable=True)
    intangible_assets_and_goodwill = Column(Float, nullable=True)
    goodwill = Column(Float, nullable=True)
    tangible_fixed_assets = Column(Float, nullable=True)
    right_of_use_assets = Column(Float, nullable=True)
    long_term_receivables = Column(Float, nullable=True)
    long_term_investments = Column(Float, nullable=True)
    other_fixed_assets = Column(Float, nullable=True)
    current_assets = Column(Float, nullable=True)
    inventories = Column(Float, nullable=True)
    short_term_receivables = Column(Float, nullable=True)
    short_term_investments = Column(Float, nullable=True)
    cash_and_cash_equivalents = Column(Float, nullable=True)
    other_current_assets = Column(Float, nullable=True)
    assets_held_for_sale = Column(Float, nullable=True)
    total_assets = Column(Float, nullable=True)
    equity_attributable_to_owners_of_parent = Column(Float, nullable=True)
    share_capital = Column(Float, nullable=True)
    treasury_shares = Column(Float, nullable=True)
    reserve_capital = Column(Float, nullable=True)
    non_controlling_interests = Column(Float, nullable=True)
    long_term_liabilities = Column(Float, nullable=True)
    trade_payables = Column(Float, nullable=True)
    loans_and_borrowings = Column(Float, nullable=True)
    debt_securities_issued = Column(Float, nullable=True)
    lease_liabilities = Column(Float, nullable=True)
    other_long_term_liabilities = Column(Float, nullable=True)
    short_term_liabilities = Column(Float, nullable=True)
    trade_payables_short_term = Column(Float, nullable=True)
    loans_and_borrowings_short_term = Column(Float, nullable=True)
    debt_securities_issued_short_term = Column(Float, nullable=True)
    lease_liabilities_short_term = Column(Float, nullable=True)
    other_short_term_liabilities = Column(Float, nullable=True)
    accruals_and_deferred_income = Column(Float, nullable=True)
    total_liabilities_and_equity = Column(Float, nullable=True)


engine = create_engine("sqlite:///database/stocks.db")
Base.metadata.create_all(engine)
