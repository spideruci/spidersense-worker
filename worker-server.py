from flask import Flask
from flask_graphql import GraphQLView
import graphene
import pymysql
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, foreign
import schema
import models
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:313461@127.0.0.1:3306/spider-worker'
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

models.Base.metadata.create_all(engine)

#navicat script
# ./navicat15-mysql-en.AppImage
app = Flask(__name__)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql',
    schema=schema.schema, graphiql=True,get_context=lambda: {'session':session}))


if __name__ == '__main__':
    app.run()
