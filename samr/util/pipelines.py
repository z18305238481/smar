# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.dialects.mysql.types import INTEGER, DATETIME, VARCHAR, DECIMAL, TEXT, BIGINT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import reflection

# from configparser import ConfigParser
# cf = ConfigParser()
# cf.read("config.ini")

# host = cf.get("Mysql-Database", "host")
# port = cf.get("Mysql-Database", "port")
# users = cf.get("Mysql-Database", "user")
# passwd = cf.get("Mysql-Database", "passwd")
# db = cf.get("Mysql-Database", "db")
# charset = cf.get("Mysql-Database", "charset")

host = '127.0.0.1'
port = 3306
users = 'root'
passwd = ''
db = 'samr'
charset = 'utf8mb4'


def process_item(item):
    datas = dict(item)

    engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=%s' % (users, passwd, host, port, db, charset), echo=False)
    DBSession = sessionmaker(bind=engine)
    Base = declarative_base()  # 生成ORM基类

    insp = reflection.Inspector.from_engine(engine)
    colums = insp.get_columns(item['table'])  # 获取表字段信息

    class User(Base):
        __tablename__ = item['table']  # 表名
        for i in colums:
            types = i['type']  # 字段类型
            cols = i['name']  # 列名
            if INTEGER == type(types):
                if i.get('autoincrement') == True:
                    locals()[cols] = Column(INTEGER(), primary_key=True)
                else:
                    locals()[cols] = Column(INTEGER())
            elif DATETIME == type(types):
                locals()[cols] = Column(DATETIME())
            elif VARCHAR == type(types):
                locals()[cols] = Column(VARCHAR())
            elif DECIMAL == type(types):
                locals()[cols] = Column((DECIMAL()))
            elif TEXT == type(types):
                locals()[cols] = Column((TEXT()))
            elif BIGINT == type(types):
                locals()[cols] = Column((BIGINT()))

    # Base.metadata.create_all(engine)  # 初始化
    user = User()

    # 插入数据
    cursor = DBSession()  # session实例
    for key in datas:
        setattr(user, key, datas[key])

    cursor.add(user)

    try:
        cursor.commit()
    except Exception as err:
        if 'Duplicate' in str(err):
            print('唯一键重复异常')
