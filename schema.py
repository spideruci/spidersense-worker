from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene import relay
import graphene

import models


class ProjectQuery(SQLAlchemyObjectType):
    class Meta:
        model = models.Project


class BuildQuery(SQLAlchemyObjectType):
    class Meta:
        model = models.Build

class TestCaseQuery(SQLAlchemyObjectType):
    class Meta:
        model = models.TestCase

class LineQuery(SQLAlchemyObjectType):
    class Meta:
        model = models.Line

class CoverageQuery(SQLAlchemyObjectType):
    class Meta:
        model = models.Coverage

class Query(graphene.ObjectType):
    projects = graphene.List(ProjectQuery,projectId=graphene.Int(default_value=None),projectName=graphene.String(default_value=None))

    builds = graphene.List(BuildQuery, projectId=graphene.Int(default_value=None), buildId=graphene.Int(),
                           commitId=graphene.String(default_value=None))

    testcases = graphene.List(TestCaseQuery, testcaseId=graphene.Int(), projectId=graphene.Int(),buildId=graphene.Int(),
                              sourceName=graphene.String())

    lines = graphene.List(LineQuery, lineId=graphene.Int(), sourceName=graphene.String(), projectId=graphene.Int(),buildId=graphene.Int())

    coverages = graphene.List(CoverageQuery, lineId=graphene.Int(), testcaseId=graphene.Int())

    def resolve_projects(self, info, **kwargs):#operate given arguments
        query = ProjectQuery.get_query(info)  # SQLAlchemy query
        if (kwargs.get("projectId")):
            query=query.filter(models.Project.projectId==kwargs.get("projectId"))
        if (kwargs.get("projectName")):
            query=query.filter(models.Project.projectName==kwargs.get("projectName"))
        return query.all()

    def resolve_builds(self, info, **kwargs):
        query = BuildQuery.get_query(info)
        if(kwargs.get("projectId")):
            query=query.filter(models.Build.projectId==kwargs.get('projectId'))
        if (kwargs.get("buildId")):
            query = query.filter(models.Build.buildId == kwargs.get('buildId'))
        if (kwargs.get("commitId")):
            query=query.filter(models.Build.commitId==kwargs.get("commitId"))
        return query.all()

    def resolve_testcases(self,info,**kwargs):
        query = TestCaseQuery.get_query(info)
        if(kwargs.get('testcaseId')):
            query=query.filter(models.TestCase.testcaseId==kwargs.get('testcaseId'))
        if (kwargs.get('projectId')):
            query = query.filter(models.TestCase.projectId == kwargs.get('projectId'))
        if (kwargs.get('sourceName')):
            query = query.filter(models.TestCase.sourceName == kwargs.get('sourceName'))
        if (kwargs.get('buildId')):
            query = query.filter(models.TestCase.buildId == kwargs.get('buildId'))
        return query.all()

    def resolve_lines(self,info,**kwargs):
        query = LineQuery.get_query(info)
        if (kwargs.get('lineId')):
            query = query.filter(models.Line.lineId == kwargs.get('lineId'))
        if (kwargs.get('sourceName')):
            query = query.filter(models.Line.sourceName == kwargs.get('sourceName'))
        if (kwargs.get('projectId')):
            query = query.filter(models.Line.projectId == kwargs.get('projectId'))
        if (kwargs.get('buildId')):
            query = query.filter(models.Line.buildId == kwargs.get('buildId'))
        return query.all()

    def resolve_coverages(self,info, **kwargs):
        query = CoverageQuery.get_query(info)
        if (kwargs.get('lineId')):
            query = query.filter(models.Coverage.lineId == kwargs.get('lineId'))
        if (kwargs.get('testcaseId')):
            query = query.filter(models.Coverage.testcaseId == kwargs.get('testcaseId'))
        return query.all()

schema = graphene.Schema(query=Query)