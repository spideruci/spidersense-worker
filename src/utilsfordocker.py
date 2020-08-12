#!/usr/bin/python
import json
import sys
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, Integer, String, ForeignKey,Float
from sqlalchemy.orm import relationship, foreign

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class Project(Base):
    __tablename__ = 'project'
    projectId = Column(Integer(), primary_key=True)
    projectName = Column(String(256))
    projectLink = Column(String())
    builds = relationship('Build',uselist=True)
    testcase = relationship('TestCase', uselist=True)

class Build(Base):
    __tablename__ = 'build'
    buildId = Column(Integer(), primary_key=True)
    projectId = Column(Integer(),ForeignKey('project.projectId'))
    commitId = Column(String(256))
    committer=Column(String())
    message=Column(String())
    timestamp=Column(Float())
    project = relationship(
        'Project',
        primaryjoin=(projectId == foreign(Project.projectId)),
        uselist=False,
    )
    testcase = relationship('TestCase', uselist=True)
    line = relationship('Line', uselist=True)

class TestCase(Base):
    __tablename__ = 'testcase'
    testcaseId = Column(Integer(),primary_key=True)
    projectId = Column(Integer(), ForeignKey('project.projectId'))
    buildId = Column(Integer(), ForeignKey('build.buildId'))
    sourceName = Column(String(256))
    signature = Column(String(256))
    passed = Column(Integer())
    #coveredLines=Column(String())
    project = relationship(
        'Project',
        primaryjoin=(projectId == foreign(Project.projectId)),
        uselist=False,
    )
    build = relationship(
        'Build',
        primaryjoin=(buildId == foreign(Build.buildId)),
        uselist=False,
    )
    coverage = relationship('Coverage', uselist=True)

class Line(Base):
    __tablename__ = 'line'
    lineId = Column(Integer(), primary_key=True)
    projectId = Column(Integer(), ForeignKey('project.projectId'))
    buildId = Column(Integer(), ForeignKey('build.buildId'))
    sourceName = Column(String(256))
    lineNumber = Column(Integer())
    #testcaseIds = Column(String())
    project = relationship(
        'Project',
        primaryjoin=(projectId == foreign(Project.projectId)),
        uselist=False,
    )
    build = relationship(
        'Build',
        primaryjoin=(buildId == foreign(Build.buildId)),
        uselist=False,
    )
    coverage = relationship('Coverage', uselist=True)

class Coverage(Base):
    __tablename__ = 'coverage'
    lineId = Column(Integer(), ForeignKey('line.lineId'), primary_key=True)
    testcaseId = Column(Integer(), ForeignKey('testcase.testcaseId'), primary_key=True)
    testcase = relationship('TestCase', primaryjoin=(testcaseId == foreign(TestCase.testcaseId)), uselist=False)
    line = relationship('Line', primaryjoin=(lineId == foreign(Line.lineId)), uselist=False)

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:313461@172.17.0.1:3306/spider-worker'
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def database_operation(projectId,buildId,jsonpath):
    if os.path.exists(jsonpath):
        f = open(jsonpath, 'r', encoding='utf-8')
        dict_data = json.load(f)
        testCount = dict_data['testCount']
        testList = dict_data['testsIndex']
        testList.pop(-1)
        tList = []
        for test in testList:
            # only signature
            newCase = TestCase(projectId=projectId, buildId=buildId, sourceName=test.split('/')[1],
                                      signature=test.split('/', 2)[-1], passed=1)
            tList.append(newCase)
        session.bulk_save_objects(tList)
        session.commit()
        #
        sourceList = dict_data['sources']
        for src in sourceList:
            fullname=src['source']['fullName']
            startLine=src['source']['firstLine']
            coverableLines=src['coverableLines']
            lines = []
            for lineindex in range(len(coverableLines)):
                if coverableLines[lineindex]==True:
                    newLine=Line(projectId=projectId, buildId=buildId,sourceName=fullname,lineNumber=startLine+lineindex)
                    lines.append(newLine)
            session.bulk_save_objects(lines)
            session.commit()
            lines.clear()


        testIdDict = {}  # only one query, put it in the dict, less connect to database
        testIdandLines = {}
        testIdList = []
        currTestListplusId = session.query(TestCase).filter(TestCase.projectId == projectId,
                                                                   TestCase.buildId==buildId).all()
        for cases in currTestListplusId:
            string = cases.sourceName + cases.signature
            testIdDict[string] = cases.testcaseId
            testIdandLines[cases.testcaseId] = []
            testIdList.append(cases.testcaseId)


        lineIdDict = {}
        lineIdandTestcases = {}
        lineIdList = []
        currLineListplusId = session.query(Line).filter(Line.projectId == projectId,
                                                                   Line.buildId==buildId).all()
        for lines in currLineListplusId:
            string = lines.sourceName + str(lines.lineNumber)
            lineIdDict[string] = lines.lineId
            lineIdandTestcases[lines.lineId] = []
            lineIdList.append(lines.lineId)



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
                        newCoverage = Coverage(lineId=lineId, testcaseId=testcaseId)
                        covlist.append(newCoverage)
            session.bulk_save_objects(covlist)  # bulk save
            session.commit()
            covlist.clear()

        print('build '+str(buildId)+' analyze over!')
    else:
        print('no such file')
pid=sys.argv[1]
bid=sys.argv[2]
path=sys.argv[3]

database_operation(pid,bid,path)
