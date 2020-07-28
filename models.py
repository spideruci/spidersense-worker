from sqlalchemy import Column, Integer, String, ForeignKey
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


