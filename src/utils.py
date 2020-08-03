import json
import os
from src import models
import requests
import time

def database_operation(projectId,buildId,jsonpath,session):
    if os.path.exists(jsonpath):
        f = open(jsonpath, 'r', encoding='utf-8')
        dict_data = json.load(f)
        testList = dict_data['testsIndex']
        testList.pop(-1)
        tList = []
        for test in testList:
            # only signature
            newCase = models.TestCase(projectId=projectId, buildId=buildId, sourceName=test.split('/')[1],
                                      signature=test.split('/', 2)[-1], passed=1)
            tList.append(newCase)
        print('testcase over!')
        session.bulk_save_objects(tList)
        session.commit()

        sourceList = dict_data['sources']

        saveLines(sourceList,projectId,buildId,session)

        testIdDict=makeTestDict(session,projectId,buildId)

        lineIdDict=makeLineDict(session,projectId,buildId)

        for src in sourceList:
            fullname = src['source']['fullName'].replace('/','.')
            startLine = src['source']['firstLine']
            covlist = []
            activeTests = src['activatingTests']  # index in the list
            testcaseindex = 0
            for tests in activeTests:
                matrix = src['testStmtMatrix'][testcaseindex]  # single matrix
                testcaseinfo = testList[tests]
                testcaseId = testIdDict[testcaseinfo.split('/')[1] + testcaseinfo.split('/', 2)[-1]]
                for l in range(len(matrix)):
                    if matrix[l] == True:
                        lineId = lineIdDict[fullname + str(l + startLine)]
                        newCoverage = models.Coverage(lineId=lineId, testcaseId=testcaseId)
                        covlist.append(newCoverage)
            session.bulk_save_objects(covlist)  # bulk save
            session.commit()
            covlist.clear()
            print(fullname+' success!')

            # for src in sourceList:
            #     fullname = src['source']['fullName']
            #     print(fullname)
            #     startLine = src['source']['firstLine']
            #     covlist = []
            #     activeTests = src['activatingTests']  # index in the list
            #     testcaseindex = 0
            #     for tests in activeTests:
            #         matrix=src['testStmtMatrix'][testcaseindex]#single matrix
            #         testcaseinfo=testList[tests]
            #         # testcaseId=session.query(models.TestCase).filter(models.TestCase.sourceName==testcaseinfo.split('/')[1],
            #         #                                                  models.TestCase.signature==testcaseinfo.split('/',2)[-1],
            #         #                                                  models.TestCase.projectId==2).first().testcaseId
            #         testcaseId=testIdDict[testcaseinfo.split('/')[1]+testcaseinfo.split('/',2)[-1]]
            #         for l in range(len(matrix)):
            #             if matrix[l]==True:
            #                 # lineId=session.query(models.Line).filter(models.Line.sourceName==fullname,models.Line.lineNumber==l+startLine,
            #                 #                                          models.Line.projectId==2).one().lineId
            #                 lineId=lineIdDict[fullname+str(l+startLine)]
            #                 testIdandLines[testcaseId].append(lineId)
            #                 lineIdandTestcases[lineId].append(testcaseId)
            # # mappingtest=[]
            # # for id in testIdList:
            # #     mappingtest.append({'testcaseId':id,'coveredLines':','.join(map(str,testIdandLines[id]))})
            # mappingline=[]
            # for id in lineIdList:
            #     mappingline.append({'lineId':id,'testcaseIds':','.join(map(str,lineIdandTestcases[id]))})
            #
            # #session.bulk_update_mappings(models.TestCase,mappingtest)
            # session.bulk_update_mappings(models.Line,mappingline)
            # session.commit()
            # print(testIdandLines)
            # print(lineIdandTestcases)
    else:
        print('no such file')


def saveLines(sourceList,projectId,buildId, session):
    for src in sourceList:
        fullname = src['source']['fullName'].replace('/', '.')
        startLine = src['source']['firstLine']
        coverableLines = src['coverableLines']
        lines = []
        for lineindex in range(len(coverableLines)):
            if coverableLines[lineindex] == True:
                newLine = models.Line(projectId=projectId, buildId=buildId, sourceName=fullname,
                                      lineNumber=startLine + lineindex)
                lines.append(newLine)
        session.bulk_save_objects(lines)
        session.commit()
        lines.clear()
        print(fullname+'lines over!')

def makeTestDict(session,projectId,buildId):
    testIdDict = {}  # only one query, put it in the dict, less connect to database
    testIdandLines = {}
    testIdList = []
    currTestListplusId = session.query(models.TestCase).filter(models.TestCase.projectId == projectId,
                                                               models.TestCase.buildId == buildId).all()
    for cases in currTestListplusId:
        string = cases.sourceName + cases.signature
        testIdDict[string] = cases.testcaseId
        testIdandLines[cases.testcaseId] = []
        testIdList.append(cases.testcaseId)
    return testIdDict

def makeLineDict(session,projectId,buildId):
    lineIdDict = {}
    lineIdandTestcases = {}
    lineIdList = []
    currLineListplusId = session.query(models.Line).filter(models.Line.projectId == projectId,
                                                           models.Line.buildId == buildId).all()
    for lines in currLineListplusId:
        string = lines.sourceName + str(lines.lineNumber)
        lineIdDict[string] = lines.lineId
        lineIdandTestcases[lines.lineId] = []
        lineIdList.append(lines.lineId)
    return lineIdDict

def githubTimeConvert(gittime):
    gdate = gittime[0:10]
    gtime = gittime[11:19]
    return time.mktime(time.strptime(gdate+' '+gtime, "%Y-%m-%d %H:%M:%S"))

def githubTimeCompare(gittime1,gittime2):
    return githubTimeConvert(gittime2)>githubTimeConvert(gittime1)
#https://github.com/sunflower0309/jsoup.git
#https://api.github.com/repos/sunflower0309/jsoup/commits?per_page=2&sha=dc38b0aed68f0ece00a32dd927e56c4e50132ed9
def getcommits(author,name,time):
    commits=set()
    branches=requests.get('https://api.github.com/repos/'+author+'/'+name+'/branches').json()
    for branch in branches:
        sha=branch['commit']['sha']
        commitbr=requests.get('https://api.github.com/repos/'+author+'/'+name+'/commits?per_page=100&sha='+sha).json()
        for cm in commitbr:
            if(githubTimeConvert(cm['commit']['committer']['date'])>time):
                commits.add((cm['sha'],githubTimeConvert(cm['commit']['committer']['date'])))
                print(commits)
            else:
                break
    return commits
#getcommits(1,'2019-07-05T03:38:30Z')
#print(githubTimeConvert('2020-05-02T08:01:44Z'))
# for i in range(100):
#     print(i)
#     workerServer.session.add(models.Build(buildId=33+i,projectId=7,commitId=str(i)))
#     workerServer.session.commit()
#     database_operation(7, 33+i, '/home/dongxinxiang/demo/tacoco_output/jsoup-cov-matrix.json', workerServer.session)


