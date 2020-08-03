import graphene
from neo4j import neo4jModels


class LineSchema(graphene.ObjectType):
    lineid=graphene.String()
    projectId = graphene.String()
    buildId = graphene.String()
    linenumber = graphene.String()
    sourcename = graphene.String()


class TestcaseSchema(graphene.ObjectType):
    testcaseid=graphene.String()
    projectId = graphene.String()
    buildId = graphene.String()
    signature = graphene.String()
    sourcename = graphene.String()
    coverage=graphene.List(LineSchema)

    def resolve_coverage(self, info):
        return neo4jModels.Testcase().match(neo4jModels.graph).where(testcaseid=self.testcaseid).first().fetch_coverage()


class Query(graphene.ObjectType):
    Testcases = graphene.List(lambda: TestcaseSchema,testcaseid=graphene.String(default_value=None))
    Lines = graphene.List(lambda: LineSchema,lineid=graphene.String(default_value=None))


    def resolve_Testcases(self, info,**kwargs):
        #t1=time.time()
        result= neo4jModels.Testcase().all

        if(kwargs.get('testcaseid')):
            result= neo4jModels.Testcase.match(neo4jModels.graph).where(testcaseid='t' + kwargs.get('testcaseid'))#type=TestcaseMatch
        #t2=time.time()
        #print(t2-t1)
        return [TestcaseSchema(**testcase.as_dict()) for testcase in result]

    def resolve_Lines(self, info,**kwargs):
        result = neo4jModels.Line().all

        if (kwargs.get('lineid')):
            result = neo4jModels.Line.match(neo4jModels.graph).where(
                lineid=kwargs.get('lineid'))  # type=LineMatch
        return [LineSchema(**line.as_dict()) for line in result]
        #return [LineSchema(**line.as_dict()) for line in neo4jModels.Line().all]

schema = graphene.Schema(query=Query)