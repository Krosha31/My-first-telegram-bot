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
    fill = Column(BOOLEAN)


class Notification(base):
    __tablename__ = 'Notifications'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False)
    text = Column(String)
