import graphene
import neo4jModels




class LineSchema(graphene.ObjectType):
    lineid=graphene.String()

    def resolve_coverage(self, info):
        return neo4jModels.Line().match(neo4jModels.graph).where(
            lineid=self.lineid).first().fetch_coverage()

class TestcaseSchema(graphene.ObjectType):
    testcaseid=graphene.String()
    coverage=graphene.List(LineSchema)

    def resolve_coverage(self, info):
        return neo4jModels.Testcase().match(neo4jModels.graph).where(testcaseid=self.testcaseid).first().fetch_coverage()


class Query(graphene.ObjectType):
    Testcases = graphene.List(lambda: TestcaseSchema,testcaseid=graphene.String(default_value=None))
    Lines = graphene.List(lambda: LineSchema,lineid=graphene.String(default_value=None))


    def resolve_Testcases(self, info,**kwargs):
        result=neo4jModels.Testcase().all

        if(kwargs.get('testcaseid')):
            result=neo4jModels.Testcase.match(neo4jModels.graph).where(testcaseid='t'+kwargs.get('testcaseid'))#type=TestcaseMatch
        return [TestcaseSchema(**testcase.as_dict()) for testcase in result]

    def resolve_Lines(self, info,**kwargs):
        result = neo4jModels.Line().all

        if (kwargs.get('lineid')):
            result = neo4jModels.Line.match(neo4jModels.graph).where(
                lineid=kwargs.get('lineid'))  # type=LineMatch
        return [LineSchema(**line.as_dict()) for line in result]
        #return [LineSchema(**line.as_dict()) for line in neo4jModels.Line().all]

schema = graphene.Schema(query=Query)