import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
import datetime
from datetime import timedelta, datetime


engine = create_engine("sqlite:///krosha_bot.db")
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











def f():
    session = sessionmaker(bind=engine)()
    q = session.query(Notification)
    for i in q:
        print(i.user)





session = sessionmaker(bind=engine)()
k = datetime.now() - (datetime.now() - timedelta(hours=2))
print(k.seconds)
print(k)

# session = sessionmaker(bind=engine)()
# n = Notification(user=22, text='22', time=datetime.datetime.now())
# session.add(n)
# session.commit()

q = session.query(User).filter_by(chat_id=1)



