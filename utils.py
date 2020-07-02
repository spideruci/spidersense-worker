import configparser
import json
import sys
import os
import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:313461@127.0.0.1:3306/spider-worker'
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()



cf = configparser.ConfigParser()
cf.read('config.ini')
jsonpath=cf.get('filepath', 'cov-matrix-path')
print(jsonpath)
#f = open(jsonpath, 'r', encoding = 'utf-8')
if os.path.exists(jsonpath):
    f = open(jsonpath, 'r', encoding = 'utf-8')
    dict_data = json.load(f)
    testCount=dict_data['testCount']
    testList=dict_data['testsIndex']
    testList.pop(-1)
    tList=[]
    for test in testList:
        #only signature
        newCase=models.TestCase(projectId=4,buildId=1,sourceName=test.split('/')[1],signature=test.split('/',2)[-1],passed=1)
        tList.append(newCase)
    session.bulk_save_objects(tList)
    session.commit()
    #
    sourceList=dict_data['sources']
    for src in sourceList:
        fullname=src['source']['fullName']
        startLine=src['source']['firstLine']
        activeTests=src['activatingTests']#index in the list
        coverableLines=src['coverableLines']
        lines = []
        for lineindex in range(len(coverableLines)):
            if coverableLines[lineindex]==True:
                newLine=models.Line(projectId=4,buildId=1,sourceName=fullname,lineNumber=startLine+lineindex)
                lines.append(newLine)
        session.bulk_save_objects(lines)
        session.commit()
        lines.clear()


    testIdDict={}#only one query, put it in the dict, less connect to database
    currTestListplusId=session.query(models.TestCase).filter(models.TestCase.projectId==4).all()
    for cases in currTestListplusId:
        string=cases.sourceName+cases.signature
        testIdDict[string]=cases.testcaseId
    print(len(currTestListplusId))

    lineIdDict={}
    currLineListplusId=session.query(models.Line).filter(models.Line.projectId==4).all()
    for lines in currLineListplusId:
        string=lines.sourceName+str(lines.lineNumber)
        lineIdDict[string]=lines.lineId
    print(len(currLineListplusId))

    for src in sourceList:
        fullname = src['source']['fullName']
        print(fullname)
        startLine = src['source']['firstLine']
        covlist = []
        activeTests = src['activatingTests']  # index in the list
        testcaseindex = 0
        for tests in activeTests:
            matrix=src['testStmtMatrix'][testcaseindex]#single matrix
            testcaseinfo=testList[tests]
            # testcaseId=session.query(models.TestCase).filter(models.TestCase.sourceName==testcaseinfo.split('/')[1],
            #                                                  models.TestCase.signature==testcaseinfo.split('/',2)[-1],
            #                                                  models.TestCase.projectId==2).first().testcaseId
            testcaseId=testIdDict[testcaseinfo.split('/')[1]+testcaseinfo.split('/',2)[-1]]
            for l in range(len(matrix)):
                if matrix[l]==True:
                    # lineId=session.query(models.Line).filter(models.Line.sourceName==fullname,models.Line.lineNumber==l+startLine,
                    #                                          models.Line.projectId==2).one().lineId
                    lineId=lineIdDict[fullname+str(l+startLine)]
                    newCoverage=models.Coverage(lineId=lineId,testcaseId=testcaseId)
                    print(lineId," ",testcaseId)
                    covlist.append(newCoverage)
        session.bulk_save_objects(covlist)#bulk save
        session.commit()
        covlist.clear()