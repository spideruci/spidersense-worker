from flask import Flask,request
from flask_graphql import GraphQLView
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import schema
import buildProj
import models
import configparser
import utils
import json
from sqlalchemy.ext.declarative import declarative_base

from github_webhook import Webhook
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:313461@127.0.0.1:3306/spider-worker'#change this to your own sql connection
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
cf = configparser.ConfigParser()
cf.read('config.ini')

models.Base.metadata.create_all(engine)

#utils.database_operation(buildId=17,projectId=10,session=session,jsonpath='/home/dongxinxiang/tarantula-cov-matrix.json')

# navicat script
# ./navicat15-mysql-en.AppImage
app = Flask(__name__)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

webhook = Webhook(app) # Defines '/postreceive' endpoint
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql',
    schema=schema.dataschema,graphiql=True,get_context=lambda: {'session':session}))

def operate_proj(git):
    os.system('rm -rf /home/dongxinxiang/demo/*')
    exist, buildId, projId, name = buildProj.build(git)
    print('get '+name)
    if exist == True:
        pass
    else:
        jsonpath = cf.get('filepath', 'cov-matrix-path') + name + '-cov-matrix.json'
        utils.database_operation(projId, buildId, jsonpath, session)
    os.system('rm -rf /home/dongxinxiang/tacoco/tacoco_output/*')

#utils.database_operation(projectId=13,buildId=21,jsonpath='/home/dongxinxiang/demo/tacoco_output/Tarantula-cov-matrix.json',session=session)

@app.route('/test/project/<projectId>')
def projQuery(projectId):
    query = "{projects(projectId:"+projectId+"){ projectName projectLink}}"
    print(projectId)
    result = schema.dataschema.execute(query,context_value={'session': session})
    d = json.dumps(result.data)
    print('{}'.format(d))
    return '{}'.format(d)

@app.route('/getTaranCoverage')
def TaranQuery():
    query = "{builds(buildId:17){ line {lineId lineNumber sourceName coverage { testcase { testcaseId sourceName signature }}}}}"
    result = schema.dataschema.execute(query,context_value={'session': session})
    d = json.dumps(result.data)
    print('{}'.format(d))
    return '{}'.format(d)
# if os.environ.get('WERKZEUG_RUN_MAIN') != 'true': #when restart the server, get the latest version
#     os.system('rm -rf /home/dongxinxiang/demo/*')
#     projList=cf.get('webhook-proj','proj-list').split(',')
#     for proj in projList:
#         operate_proj(proj)


@webhook.hook()        # Defines a handler for the 'push' event
def on_push(data):
    # print(data['after'])
    # print(data['repository']['clone_url'])
    operate_proj(data['repository']['clone_url'])

if __name__ == '__main__':
    app.run()

