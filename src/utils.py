import json
import os
from src import models
import requests
import time
import configparser
from src import sqlsession,cfgreader
from sqlalchemy import exists

token=cfgreader.cf.get('polling','token')
headers={'Authorization': 'token '+token}

def database_operation(projectId,buildId,jsonpath,session):
    if os.path.exists(jsonpath):
        f = open(jsonpath, 'r', encoding='utf-8')
        dict_data = json.load(f)
        testList = dict_data['testsIndex']
        testList.pop(-1)
        tList = []
        for test in testList:
            # only signature
            passed=1
            if test.endswith('_F'):
                passed=0
                test=test[:-2]
            newCase = models.TestCase(projectId=projectId, buildId=buildId, sourceName=test.split('/')[1],
                                      signature=test.split('/', 2)[-1], passed=passed)
            tList.append(newCase)
        #print('testcase over!')
        session.bulk_save_objects(tList)
        session.commit()

        sourceList = dict_data['sources']

        saveLines(sourceList,projectId,buildId,session)

        testIdDict=makeTestDict(session,projectId,buildId)

        lineIdDict=makeLineDict(session,projectId,buildId)

        for src in sourceList:
            fullname = src['source']['fullName']
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
            #print(fullname+' success!')

    else:
        print('no such file')


def saveLines(sourceList,projectId,buildId, session):
    for src in sourceList:
        fullname = src['source']['fullName']
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


def getprojs():
    config = configparser.ConfigParser()
    config.read(cfgreader.CONFIG_PATH)
    infolist = config.get("polling", "proj-list")
    proj_list = json.loads(infolist)
    keys = list(proj_list.keys())
    return keys,proj_list


def getcommits(author,name,gtime):
    commits=set()
    print(author,name)
    branches=requests.get('https://api.github.com/repos/'+author+'/'+name+'/branches',headers=headers).json()
    for branch in branches:
        sha=branch['commit']['sha']
        commitbr=requests.get('https://api.github.com/repos/'+author+'/'+name+'/commits?per_page=100&sha='+sha,headers=headers).json()
        for cm in commitbr:
            if(githubTimeConvert(cm['commit']['committer']['date'])>gtime):

                commits.add((cm['sha'],githubTimeConvert(cm['commit']['committer']['date']),cm['commit']['committer']['name'],
                             cm['commit']['message']))
            else:
                break
    return commits

def getNewProjcommits(author,name):
    commits=set()
    branches=requests.get('https://api.github.com/repos/'+author+'/'+name+'/branches?per_page=1000',headers=headers).json()
    for branch in branches:
        sha=branch['commit']['sha']
        #print(sha)
        commitbr=requests.get('https://api.github.com/repos/'+author+'/'+name+'/commits?per_page=1&sha='+sha,headers=headers).json()
        for cm in commitbr:
            #print(time.time()-githubTimeConvert(cm['commit']['committer']['date']))
            if time.time()-githubTimeConvert(cm['commit']['committer']['date'])<7776000:#deprecate too old commits,older than 90 days
                commits.add(
                    (cm['sha'], githubTimeConvert(cm['commit']['committer']['date']), cm['commit']['committer']['name'],
                     cm['commit']['message']))
    return commits


def getAllCommits():
    allCommits= {}
    users,projlist=getprojs()
    print(users,projlist)
    for user in users:
        for name in projlist[user]:
            link = 'https://github.com/' + user + '/' + name + '.git'
            print(link)
            if sqlsession.session.query(exists().where(models.Project.projectLink == link)).scalar() == False:
                newProj = models.Project(projectName=name, projectLink=link)
                sqlsession.session.add(newProj)
                sqlsession.session.commit()

            projid=sqlsession.session.execute('select projectId from project where projectLink="'
                                                     + link +'"').fetchone()[0]
            lasttime=sqlsession.session.execute('select timestamp from build where projectId='
                                                     + str(projid) +' order by timestamp desc').fetchone()
            if lasttime==None:
                commit=getNewProjcommits(user,name)
                print(len(commit))
                allCommits[link] = commit
            else:
                commit = getcommits(user, name, lasttime[0])
                print(len(commit))
                allCommits[link] = commit
    print(allCommits)
    return allCommits

def getAutherandRepoFromGit(gitLink):
    author=gitLink.split('/')[-2]
    name=gitLink.split('/')[-1].split('.')[0]
    return author,name


