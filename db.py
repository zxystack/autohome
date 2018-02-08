# *-* coding=utf8 *-*

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

def init_metadata(engine, db_name):
    engine.execute("create database if not exists %s"%db_name)
    engine.execute("create table if not exists {db_name}.metadata (name varchar(64) primary key, value int);".format(db_name=db_name))
    try:
        engine.execute("insert into {db_name}.metadata (name, value) values ('version', 0);".format(db_name=db_name))
    except Exception:
        pass 

class Metadata(object):

    def __init__(self, session):
        self.session = session 

    def get(self, name):
        row = self.session.execute("select value from metadata where name='{name}'".format(name=name)).first()
        return row.value if row else 0 

    def set(self, name, value):
        result = self.session.execute("update metadata set value={value} where name='{name}';".format(value=value, name=name))
        self.session.commit()
        if result.rowcount == 0:
            sql = "insert into metadata (name, value) values ('%s', %d)"%("version", value)
            self.session.commit()


def connect(host, port, username, password, db_name, upgrade, version):
    url = "mysql://{username}:{password}@{host}:{port}/?charset=utf8".format(username=username, password=password, host=host, port=port)
    engine = create_engine(url)
    init_metadata(engine, db_name)
    url = "mysql://{username}:{password}@{host}:{port}/{db_name}?charset=utf8".format(username=username, password=password, host=host, port=port, db_name=db_name)
    engine = create_engine(url)
    session = sessionmaker(bind=engine)()
    session.execute("select * from metadata for update")
    session.metadata = Metadata(session)
    current_version = session.metadata.get('version')
    if current_version < version:
        upgrade(session, current_version)
        session.metadata.set('version', version)
    return session 

VERSION = 6
def upgrade(session, current_version):
    if current_version < 2:
        session.execute(''' create table cars (
                    id  varchar(64) primary key,
                    link varchar(256),
                    brand varchar(128)
                    )ENGINE=InnoDB CHARSET=utf8;
            ''')
    if current_version < VERSION:
        session.execute('''
            create table cars_info (
               id varchar(128) primary key,
               car_id varchar(128),
               brand varchar(128),
               car_model varchar(256),
               sub_link varchar(128),
               level varchar(128),
               struct varchar(128),
               speed_changing_box varchar(128),
               engine varchar(128),
               colors varchar(128),
               low varchar(64),
               high varchar(64),
               grade varchar(64)
            )ENGINE=InnoDB CHARSET=utf8;
        ''')

session = connect("localhost", 3306, "root", 123456, "cars", upgrade, VERSION)
Base = declarative_base()

class Cars(Base):
    __tablename__  = 'cars'
    id = Column(String, primary_key=True)
    link = Column(String)
    brand = Column(String)

class CarsInfo(Base):
    __tablename__ = 'cars_info'
    id = Column(String, primary_key=True)
    car_id = Column(String)
    brand = Column(String)
    car_model = Column(String)
    sub_link = Column(String)
    level = Column(String)
    struct = Column(String)
    speed_changing_box = Column(String)
    engine = Column(String)
    colors = Column(String)
    low = Column(String)
    high = Column(String)
    grade = Column(String)