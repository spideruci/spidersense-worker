from flask import Flask, request
from flask_graphql import GraphQLView
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import schema
import buildProj
import models
import configparser
import json
import neo4jSchema
import neo4jSchema2
from sqlalchemy.ext.declarative import declarative_base
import subprocess
from github_webhook import Webhook
import time
import random
from flask import Flask
from flask_cors import CORS

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:313461@127.0.0.1:3306/spider-worker'  # change this to your own sql connection
engine = create_engine(SQLALCHEMY_DATABASE_URI,max_overflow=50,  # 超过连接池大小外最多创建的连接
        pool_size=1000,  # 连接池大小
        pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
        pool_recycle=-1)
Session = sessionmaker(bind=engine)
session = scoped_session(Session)
#session = Session()
cf = configparser.ConfigParser()
cf.read('config.ini')

models.Base.metadata.create_all(engine)

# utils.database_operation(buildId=17,projectId=10,session=session,jsonpath='/home/dongxinxiang/tarantula-cov-matrix.json')

# navicat script
# ./navicat15-mysql-en.AppImage
app = Flask(__name__)
cors = CORS(app)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

webhook = Webhook(app)  # Defines '/postreceive' endpoint
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql',
                                                           schema=neo4jSchema.schema, graphiql=True,
                                                           get_context=lambda: {'session': session}))



def operate_proj(git, commit):
    exist, buildId, projId, name = buildProj.build(git,commit)
    print('get ' + name)
    if exist == True:
        pass
    else:
        subprocess.Popen('docker run --rm spider-container:1.0 /home/run-spider-worker ' + git + ' ' + commit +
                  ' ' + str(projId) + ' ' + str(buildId),shell=True)


# utils.database_operation(projectId=13,buildId=21,jsonpath='/home/dongxinxiang/demo/tacoco_output/Tarantula-cov-matrix.json',session=session)

@app.route('/test/project/<projectId>')
def projQuery(projectId):
    query = "{projects(projectId:" + projectId + "){ projectName projectLink}}"
    print(projectId)
    result = schema.dataschema.execute(query, context_value={'session': session})
    d = json.dumps(result.data)
    session.remove()
    return '{}'.format(d)


@app.route('/getTaranCoverage')
def TaranQuery():
    query = "{builds(buildId:25){ line {lineId lineNumber sourceName coverage { testcase { testcaseId sourceName signature }}}}}"
    result = schema.dataschema.execute(query, context_value={'session': session})
    d = json.dumps(result.data)
    session.remove()
    return '{}'.format(d)


@app.route('/testcaseCoverage/<testcaseId>')
def TestcaseQuery(testcaseId):
    query = "{testcases(testcaseId:" + testcaseId + "){signature sourceName coverage{line{lineId lineNumber sourceName}}}}"
    result = schema.dataschema.execute(query, context_value={'session': session})
    d = json.dumps(result.data)
    session.remove()
    return '{}'.format(d)


@app.route('/lineCoverage/<lineId>')
def LineQuery(lineId):
    query = "{lines(lineId:" + lineId + "){lineNumber sourceName coverage{testcase{testcaseId signature sourceName}}}}"
    result = schema.dataschema.execute(query, context_value={'session': session})
    d = json.dumps(result.data)
    session.remove()
    return '{}'.format(d)


@app.route('/sourceCoverage/<sourceFile>')
def sourceQuery(sourceFile):
    query = '{lines(sourceName:"' + sourceFile + '"){lineId lineNumber coverage{testcase{testcaseId signature sourceName}}}}'
    print(query)
    result = schema.dataschema.execute(query, context_value={'session': session})
    d = json.dumps(result.data)
    session.remove()
    return '{}'.format(d)

@app.route('/var/test')
def varQuery():
    query = 'query q($srcname:String,$testId:Int){testcases(sourceName:$srcname,testcaseId:$testId){testcaseId projectId signature coverage{ line{ lineId lineNumber sourceName}}}}'
    print(query)
    result = schema.dataschema.execute(query, context_value={'session': session},variables={'srcname':'[runner:org.spideruci.tarantula.TestCalculatePassOnStmtAndFailOnStmt]',
                                                                                            'testId':10346})
    d = json.dumps(result.data)
    print('{}'.format(d))
    return '{}'.format(d)

@app.route('/getAllTaranTestcases')
def groupBySource():
    sources=session.execute('select DISTINCT sourceName from testcase where projectId=17').fetchall()
    #print(sources)
    query='{'
    index=0
    for src in sources:
        srcname=src[0]
        qname=src[0].split('.')[-1][:-1]
        subq=qname+':testcases(sourceName:"'+srcname+'"){testcaseId signature}'
        query+=subq
    query+='}'
    print(query)
    result = schema.dataschema.execute(query, context_value={'session': session})
    result.data['src']=[src[0].split('.')[-1][:-1] for src in sources]
    d = json.dumps(result.data)
    return '{}'.format(d)


@app.route('/neo4jtimetest/<tid>')
def neotest(tid):
    query='{Testcases(testcaseid:"'+str(tid)+'"){projectId signature sourcename coverage{ lineid linenumber sourcename}}}'
    result = neo4jSchema.schema.execute(query)
    d = json.dumps(result.data)
    return '{}'.format(d)

@app.route('/mysqltimetest/<tid>')
def mysqltest(tid):
    query = "{testcases(testcaseId:" + str(tid) + "){projectId signature sourceName coverage{line{lineId lineNumber sourceName}}}}"
    #query='{Testcases(testcaseid:'+str(tid)+'){projectId signature sourcename coverage{ line{lineid linenumber sourcename}}}}'
    result = schema.dataschema.execute(query, context_value={'session': session})
    d = json.dumps(result.data)
    return '{}'.format(d)
# q2:testcases(sourceName:"[runner:org.spideruci.tarantula.TestCalculatePassOnStmtAndFailOnStmt]"){testcaseId signature}
# if os.environ.get('WERKZEUG_RUN_MAIN') != 'true': #when restart the server, get the latest version
#     os.system('rm -rf /home/dongxinxiang/demo/*')
#     projList=cf.get('webhook-proj','proj-list').split(',')
#     for proj in projList:
#         operate_proj(proj)
# i=0
# for i in range(100):
#     rd=random.randint(20000,90000)
#     print(rd)
#     t1=time.time()
#     #mysqltest(rd)
#     neotest(rd)
#     t2=time.time()
#     i+=t2-t1
# print(i)

# utils.database_operation(projectId=17,buildId=25,jsonpath='/home/dongxinxiang/demo/tacoco_output/Tarantula-cov-matrix.json',session=session)
@webhook.hook()  # Defines a handler for the 'push' event
def on_push(data):
    # print(data['after'])
    # print(data['repository']['clone_url'])
    operate_proj(data['repository']['clone_url'], data['after'])


if __name__ == '__main__':
    app.run()
