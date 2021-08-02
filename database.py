import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker


engine = create_engine("sqlite:///krosha_bot.db")
session = sessionmaker(bind=engine)()


base = declarative_base()


class User(base):
    __tablename__ = 'Users'
    chat_id = Column(Integer, primary_key=True)
    timezone = Column(Integer)
    city = Column(String)
    fill = Column(BOOLEAN)
    lat = Column(Integer)
    lon = Column(Integer)


class Notes(base):
    __tablename__ = 'Notes'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, nullable=False)
    name = Column(String)
    text = Column(String)
