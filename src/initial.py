from src import workerServer,utils,sqlsession,models,schema
import json
import time
import docker
from concurrent.futures import ThreadPoolExecutor
# workerServer.operate_proj('https://github.com/sunflower0309/gson.git','ebd311ff5467a4909163a20212a284bcf1824023',utils.githubTimeConvert('2020-07-29T09:59:24Z'))
# workerServer.operate_proj('https://github.com/sunflower0309/gson.git','acb8361f7a0bbf399b9ec81beb219cc40b22a07c',utils.githubTimeConvert('2020-07-29T07:28:50Z'))
# workerServer.operate_proj('https://github.com/sunflower0309/jsoup.git','dc38b0aed68f0ece00a32dd927e56c4e50132ed9'
#                           ,utils.githubTimeConvert('2020-07-20T21:36:02Z'))
# workerServer.operate_proj('https://github.com/spideruci/Tarantula.git','7882a7c1925ae5092fade009fc7cc9f39309da82',
#                           utils.githubTimeConvert('2015-06-02T21:36:02Z'),'VijayKrishna Palepu','Using the PassFailPair\'s in the Localizer\'s API.')
# workerServer.operate_proj('https://github.com/spideruci/Tarantula.git','b9518b0e4a9e5872824e25a290f2f04a72991f1c',
#                           utils.githubTimeConvert('2015-06-03T03:00:13Z'),'VijayKrishna Palepu','Basic DataBuilder tests.')
# import requests
# print(requests.get('https://api.github.com/rate_limit',headers=utils.headers).json())
# requests.get('https://api.github.com/repos/'+'sunflower0309'+'/'+'commons-io'+'/branches',headers=utils.headers).json()
# print(requests.get('https://api.github.com/rate_limit',headers=utils.headers).json())
#workerServer.poll()
# ses=sqlsession.session
# ses.query(models.Build).filter(models.Build.buildId==29).delete()
# ses.commit()
# utils.getPullRequests('google','gson')
session = sqlsession.session
def CommitCoverageQuery(sha):
    bId = session.execute('select buildId from build where commitId=\'' + sha + '\'').fetchone()[0]
    query = "{testcases(buildId:7){signature coverage{line{lineId lineNumber sourceName}}}}"
    result = schema.dataschema.execute(query, context_value={'session': session})
    d = json.dumps(result.data)
    session.remove()
    return '{}'.format(d)
def CommitCoverageQuery1(sha):
    bId = session.execute('select buildId from build where commitId=\'' + sha + '\'').fetchone()[0]
    #query = "{builds(buildId:"+str(bId)+"){testcase{signature sourceName coverage{line{lineId lineNumber sourceName}}}}}"
    tcases=session.execute('select testcaseId from testcase where buildId='+str(bId)+'').fetchall()
    res={}
    testcases=[]
    for t in tcases:
        j1={}
        j1['testcaseId']=t[0]
        j2=[]
        coverage=session.execute('SELECT line.lineId,lineNumber,sourceName FROM coverage LEFT JOIN line on coverage.lineId=line.lineId where testcaseId='+str(t[0])).fetchall()
        for c in coverage:
            #print(c[0])
            j3={'lineId':c[0],"lineNumber":c[1],'sourceName':c[2]}
            j4={'line':j3}
            j2.append(j4)
        j1['coverage']=j2
        testcases.append(j1)
    res['testcases']=testcases
    return res
def BatchQuery1():
    tcases=[]
    res={}
    for t in tcases:
        testinfo={}
        coverage=[]
        coverageres=session.execute('SELECT line.lineId,lineNumber,sourceName FROM coverage LEFT JOIN line on coverage.lineId=line.lineId where testcaseId='+str(t)).fetchall()
        for c in coverageres:
            cov={'lineId':c[0],"lineNumber":c[1],'sourceName':c[2]}
            outercov={'line':cov}
            coverage.append(outercov)
        testinfo['coverage']=coverage
        otherinfo=session.execute('select sourceName,passed,signature from testcase where testcaseId='+str(t)).fetchone()[0]
        testinfo['sourceName']=otherinfo[0]
        testinfo['passed']=otherinfo[1]
        testinfo['signature']=otherinfo[2]
        res['t'+str(t)]=testinfo
    return res
#tcases=session.execute('select testcaseId,signature,sourceName from testcase where buildId='+'226').fetchall()
import time
t1=time.time()
#print(type(tcases[0]),tcases[0])
CommitCoverageQuery('89580cc3d25d0d89ac1f46b349e5cd315883dc79')
print(time.time()-t1)
t2=time.time()
CommitCoverageQuery1('89580cc3d25d0d89ac1f46b349e5cd315883dc79')
print(time.time()-t2)
#print()
#utilsfordocker.database_operation(74,246,'/home/dongxinxiang/tacoco/tacoco_output/mid_example-cov-matrix.json')
#utils.getAllCommits()
#workerServer.dockercheck()
#print(workerServer.client.containers(all=True)[0]['Id'])
# print(time.time())
# print(utils.getNewProjcommits('apache','flink'))
# for i in range(86001,86085):
#     print(str(i)+',')