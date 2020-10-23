from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src import cfgreader

#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:313461@127.0.0.1:3306/spider-worker'  # change this to your own sql connection
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:'+cfgreader.cf.get('docker', 'password')+\
                          '@127.0.0.1:3306/'+cfgreader.cf.get('docker', 'database')
engine = create_engine(SQLALCHEMY_DATABASE_URI,max_overflow=50,  # 超过连接池大小外最多创建的连接
        pool_size=1000,  # 连接池大小
        pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
        pool_recycle=-1)
Session = sessionmaker(bind=engine)
session = scoped_session(Session)