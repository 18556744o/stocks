#!/usr/bin/env python

import ystockquote as quotes
import config
from datetime import date
from models  import Symbol, Quote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.ext.declarative import declarative_base


class Database(object):

    def __init__(self):
        """
        Set up database access
        """
        self.Base = declarative_base()
        if config.sql_password == '':
            engine_config = 'mysql://%s@%s/%s' % (config.sql_user, config.sql_hostname, config.sql_database)
        else:
            engine_config = 'mysql://%s:%s@%s/%s' % (config.sql_user, config.sql_password, config.sql_hostname, config.sql_database)
        self.Engine = create_engine(engine_config)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.Engine)


class StockDBManager(object):
    """
    Stock database management class
    """

    def __init__(self):
        """
        Get access to database
        """
        self.db = Database()
    

    def create_database(self):
        """
        Create stock database tables if they do not exist already
        """
        self.db.Base.metadata.create_all(Engine)


    def add_stock(self, ticker, name, sector=None, industry=None):
        """
        Add a stock to the stock database
        """
        ticker = ticker.lower()
        stock = Symbol(ticker, name, sector, industry)
        session = self.db.Session()
        
        if check_stock_exists(ticker,session):
            print "Stock %s already exists!" % (ticker.upper())
        else:
            print "Adding %s to database" % (ticker.upper())
            session.add(stock)
            session.add_all(download_quotes(ticker, date(1900,01,01), date.today()))
        
        session.commit()
        session.close()

    def download_quotes(self, ticker, start_date, end_date):
        """
        Get quotes from Yahoo Finance
        """
        ticker = ticker.lower()
        start = start_date.strftime("%Y%m%d")
        end = end_date.strftime("%Y%m%d")
        data = quotes.get_historical_prices(ticker, start, end)
        data = data[len(data)-1:0:-1]
        return [Quote(ticker,val[0],val[1],val[2],val[3],val[4],val[5]) for val in data]

    def update_quotes(self, ticker):
        """
        Get all missing quotes through current day for the given stock
        """
        pass

    def sync_quotes(self):
        """
        Updates quotes for all stocks through current day.
        """
        pass
    
    def check_stock_exists(self,ticker,session=None):
        """
        Return true if stock is already in database
        """
        if session is None:
            session = self.db.Session()
        exists = bool(session.query(Symbol).filter_by(Ticker=ticker.lower()).count())
        if session is None:
            session.close()
        return exists
 
    def check_quote_exists(self,ticker,date,session=None):
        if session is None:
            session = self.db.Session()
        exists = bool(session.query(Symbol).filter_by(Ticker=ticker.lower(),Date=date).count())
        if session is None:
            session.close()
        return exists
        
    def get_quotes(self, ticker, quote_date, end_date=None):
        ticker = ticker.lower()
        session = self.db.Session()
        if end_date is not None:
            query = session.query(Quote).filter(and_(Quote.Ticker == ticker, Quote.Date >= quote_date, Quote.Date <= end_date)).order_by(Quote.Date)
        else:
            query = session.query(Quote).filter(and_(Quote.Ticker == ticker, Quote.Date == quote_date))    
        session.close()
        return [quote for quote in query.all()]
    
class IntradayAPI(object):
    """
    API for accessing intraday quote data. Uses StockDBManager to get quotes that aren't yet stored locally
    """
    def __init__(self):
        self.DBManager = StockDBManager() 
    
    def get_close(self, ticker, date, end_date=None):
        """
        Return the closing price for the stock on the selected date(s)
        """
        ticker = ticker.lower()
        
    
    