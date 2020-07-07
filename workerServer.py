from flask import Flask
from flask_graphql import GraphQLView
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import schema
import buildProj
import models
import configparser
import utils
from sqlalchemy.ext.declarative import declarative_base

from github_webhook import Webhook
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:313461@127.0.0.1:3306/spider-worker'
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
cf = configparser.ConfigParser()
cf.read('config.ini')

models.Base.metadata.create_all(engine)

#navicat script
# ./navicat15-mysql-en.AppImage
app = Flask(__name__)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

webhook = Webhook(app) # Defines '/postreceive' endpoint
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql',
    schema=schema.schema, graphiql=True,get_context=lambda: {'session':session}))

def operate_proj(git):
    exist, buildId, projId, name = buildProj.build(git)
    print('get '+name)
    if exist == True:
        pass
    else:
        jsonpath = cf.get('filepath', 'cov-matrix-path') + name + '-cov-matrix.json'
        utils.database_operation(projId, buildId, jsonpath, session)
    os.system('rm -rf /home/dongxinxiang/tacoco/tacoco_output/*')

if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    os.system('rm -rf /home/dongxinxiang/demo/*')
    projList=cf.get('webhook-proj','proj-list').split(',')
    for proj in projList:
        operate_proj(proj)


@webhook.hook()        # Defines a handler for the 'push' event
def on_push(data):
    print(data)

if __name__ == '__main__':
    app.run()

