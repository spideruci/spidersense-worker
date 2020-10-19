from apscheduler.schedulers.background import BackgroundScheduler
from flask_graphql import GraphQLView
from src import models, utils, buildProj, schema,sqlsession,cfgreader
import configparser
import json
from queue import Queue
from github_webhook import Webhook
from flask import Flask,request
from flask_cors import CORS
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import docker
import time
cf = cfgreader.cf


class BoundedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers, max_waiting_tasks, *args, **kwargs):
        super().__init__(max_workers=max_workers, *args, **kwargs)
        self._work_queue = Queue(maxsize=max_waiting_tasks)
MAX_CONTAINER=int(cf.get('polling','maximum-container'))
MAX_QUEUE=int(cf.get('polling','maximum-queue'))
DOCKER_SOCK=str(cf.get('docker','sockpath'))
MAX_LIFE=int(cf.get('docker','maxlife'))
PASSWD=str(cf.get('docker','password'))
#threadPool = ThreadPoolExecutor(max_workers=MAX_CONTAINER)
session = sqlsession.session



models.Base.metadata.create_all(sqlsession.engine)



app = Flask(__name__)
cors = CORS(app)




webhook = Webhook(app)  # Defines '/postreceive' endpoint
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql',
                                                           schema=schema.dataschema, graphiql=True,
                                                           get_context=lambda: {'session': session}))

client = docker.Client(base_url=DOCKER_SOCK)

def operate_proj(git, commit,gittime,committer,message):
    exist, buildId, projId, name = buildProj.build(git, commit, gittime,committer,message)
    #print(exist,buildId,projId,name)
    if exist == True:
        pass
    else:
        print("%s threading is printed %s, %s" % (threading.current_thread().name,git,commit))
        os.system('docker run --rm --name ' +commit +' '+ cf.get('docker',
                                                 'image') + ' /home/run-spider-worker ' + git + ' ' + commit +
                  ' ' + str(projId) + ' ' + str(buildId) + ' ' + cf.get('docker', 'database')+' '+PASSWD)
        time.sleep(3)
        while 1:
            namelist=[i['Names'][0][1:] for i in client.containers(all=True)]
            if commit in namelist:
                time.sleep(3)
            else:
                break

#-d > /home/dongxinxiang/docker.log


@app.route('/mainEntry',methods=['POST'])
def executeGraphQLQuery():
    query=request.form['query']
    result = schema.dataschema.execute(query, context_value={'session': session})
    session.remove()
    return result.data

@app.route('/batchTestcaseCoverage',methods=['POST'])
def batchTestcaseQuery():
    tlist=request.form['tlist']
    query='{'
    for tid in tlist.split(','):
        query+='t'+tid+":testcases(testcaseId:" + tid + "){signature sourceName passed coverage{line{lineId lineNumber sourceName}}}"
    query+='}'
    result = schema.dataschema.execute(query, context_value={'session': session})
    session.remove()
    return result.data


@app.route('/getProject/<projectId>')
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

@app.route('/TaranMatrix')
def TaranMatrix():
    query="{lines(buildId:25){lineId sourceName lineNumber coverage{testcaseId}}}"
    result = schema.dataschema.execute(query, context_value={'session': session})
    d = json.dumps(result.data)
    session.remove()
    return '{}'.format(d)


@app.route('/testcaseCoverage/<testcaseId>')
def TestcaseQuery(testcaseId):
    query = "{testcases(testcaseId:" + testcaseId + "){signature sourceName passed coverage{line{lineId lineNumber sourceName}}}}"
    result = schema.dataschema.execute(query, context_value={'session': session})
    return result.data



@app.route('/commitCoverage/<sha>')
def CommitCoverageQuery(sha):
    bId = session.execute('select buildId from build where commitId=\'' + sha + '\'').fetchone()[0]
    query = "{builds(buildId:"+str(bId)+"){testcase{signature sourceName coverage{line{lineId lineNumber sourceName}}}}}"
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


@app.route('/getAllProjects')
def getAllProjects():
    query="{projects{projectId projectName projectLink}}"
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
    result = schema.dataschema.execute(query, context_value={'session': session}, variables={'srcname': '[runner:org.spideruci.tarantula.TestCalculatePassOnStmtAndFailOnStmt]',
                                                                                            'testId':10346})
    d = json.dumps(result.data)
    print('{}'.format(d))
    session.remove()
    return '{}'.format(d)



@app.route('/getAllTestcases/<sha>')
def groupBySourceName(sha):
    bId = session.execute('select buildId from build where commitId=\'' + sha + '\'').fetchone()[0]
    query="{testcases(buildId:" + str(bId) + "){signature sourceName testcaseId passed}}"
    result = schema.dataschema.execute(query, context_value={'session': session})
    finalresult={}
    d = json.dumps(result.data)
    dict = json.loads('{}'.format(d))
    for cases in dict['testcases']:
        if cases['sourceName'] in finalresult.keys():
            finalresult[cases['sourceName']].append({'testcaseId':cases['testcaseId'],'signature':cases['signature'],'passed':cases['passed']})
        else:
            finalresult[cases['sourceName']]=[{'testcaseId':cases['testcaseId'],'signature':cases['signature'],'passed':cases['passed']}]
    dd=json.dumps(finalresult)
    return '{}'.format(dd)

@app.route('/getCommits/<projectId>')
def getCommits(projectId):
    query="{builds(projectId:"+str(projectId)+"){commitId committer timestamp message}}"
    result = schema.dataschema.execute(query, context_value={'session': session})
    d = json.dumps(result.data)
    dict=json.loads('{}'.format(d))
    for data in dict['builds']:
        data['timestamp']=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['timestamp']))
    session.remove()
    return json.dumps(dict)

@app.route('/getSourceInfo/<sha>')
def getSourceInfo(sha):
    dict={}
    links=[]
    bpId=session.execute('select buildId,projectId from build where commitId=\''+sha+'\'').fetchall()
    src=session.execute('select distinct sourceName from line where buildId='+str(bpId[0][0])).fetchall()
    # projId=session.execute('select projectId from build where buildId=25').fetchone()[0]
    repolink=session.execute('select projectLink from project where projectId='+str(bpId[0][1])).fetchone()[0]
    author,repo=utils.getAutherandRepoFromGit(repolink)
    for sr in src:
        path=sr[0].replace('.','/')[:-5]
        srclink='https://raw.githubusercontent.com/'+author+'/'+repo+'/'+sha+\
                '/src/main/java/'+path+'.java'
        links.append(srclink)
    dict['sourceLinks']=links
    d = json.dumps(dict)
    session.remove()
    return '{}'.format(d)



@app.route('/getTaranSourceInfo')
def getTaranSourceInfo():
    dict={}
    links=[]
    src=session.execute('select distinct sourceName from line where buildId=25').fetchall()
    projId=session.execute('select projectId from build where buildId=25').fetchone()[0]
    repolink=session.execute('select projectLink from project where projectId='+str(projId)).fetchone()[0]
    author,repo=utils.getAutherandRepoFromGit(repolink)
    for sr in src:
        path=sr[0].replace('.','/')[:-5]

        srclink='https://api.github.com/repos/'+author+'/'+repo+\
                '/contents/src/main/java/'+path+'.java'
        links.append(srclink)
    dict['sourceLinks']=links
    d = json.dumps(dict)
    session.remove()
    return '{}'.format(d)

@app.route('/sourceLineCount/<sha>')
def sourceLineCount(sha):
    bId = session.execute('select buildId from build where commitId=\'' + sha + '\'').fetchone()[0]
    linecounts=session.execute('select sourceName,count(*) from line where buildId='+str(bId)+' GROUP BY sourceName').fetchall()
    dict={}
    for src in linecounts:
        dict[src[0].replace('.','/')]=src[1]
    return '{}'.format(json.dumps(dict))

@webhook.hook()  # Defines a handler for the 'push' event
def on_push(data):
    operate_proj(data['repository']['clone_url'], data['after'],utils.githubTimeConvert(data['commits'][0]['timestamp'])+25200
                                    ,data['commits'][0]['committer']['name'],data['commits'][0]['message'])

def autopolling():
    allCommits=utils.getAllCommits()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    keys=allCommits.keys()
    with BoundedThreadPoolExecutor(MAX_CONTAINER, MAX_QUEUE) as executor:
        for key in keys:
            for cm in allCommits[key]:
                time.sleep(1)
                #print(key)
                executor.submit(operate_proj,key,cm[0],cm[1],cm[2],cm[3])
            # th = threading.Thread(target=operate_proj, args=(key,cm[0],cm[1],))
            # th.start()
            #operate_proj(key,cm[0],cm[1])
            # print(cm)
    return ''

def dockercheck():
    for container in client.containers(all=True):
        if time.time()-container['Created']>=MAX_LIFE and container['Image'].startswith('sunflower0309/spider-container'):
            os.system('docker stop '+container['Id']+' && docker rm '+container['Id'])


#@app.route('/startPolling')
@app.before_first_request
def startpoll():
    # autopolling()
    scheduler = BackgroundScheduler(timezone='America/Los_Angeles')
    scheduler.start()
    scheduler.add_job(func=autopolling, trigger="interval", seconds=1800)
    scheduler.add_job(func=dockercheck, trigger="interval", seconds=60)
    scheduler.print_jobs()

@app.route('/poll')
def poll():
    autopolling()
    return 'poll'
