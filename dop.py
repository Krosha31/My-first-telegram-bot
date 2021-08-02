import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
import datetime
import requests
from datetime import timedelta, datetime
from pprint import pprint
from bs4 import BeautifulSoup as bs
import pymorphy2

morph = pymorphy2.MorphAnalyzer()
city = morph.parse('овца')[0]
city = city.inflect({'loct'})[0]
print(city)

engine = create_engine("sqlite:///krosha_bot.db")
base = declarative_base()
API_KEY = 'a9e4fc12-0564-4698-85ff-5b698414ba9e'
params = {'lat':'56.331932', 'lon':'44.023225'}
req = requests.get(url='https://api.weather.yandex.ru/v2/informers', params={'lat':'56.331932', 'lon':'44.023225'}, headers={'X-Yandex-API-Key':API_KEY})
pprint(req.json())




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
k = datetime.now() + timedelta(hours=-5)
print(k)

# session = sessionmaker(bind=engine)()
# n = Notification(user=22, text='22', time=datetime.datetime.now())
# session.add(n)
# session.commit()

q = session.query(User).filter_by(chat_id=1)



