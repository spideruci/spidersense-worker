import graphene
import neo4jModels


class TestcaseSchema2(graphene.ObjectType):
    testcaseid=graphene.String()

class LineSchema2(graphene.ObjectType):
    lineid=graphene.String()
    covered = graphene.List(TestcaseSchema2)
    def resolve_covered(self, info):
        return neo4jModels.Line().match(neo4jModels.graph).where(
            lineid=self.lineid).first().fetch_covered()







class Query2(graphene.ObjectType):
    Testcases = graphene.List(lambda: TestcaseSchema2,testcaseid=graphene.String(default_value=None))
    Lines = graphene.List(lambda: LineSchema2,lineid=graphene.String(default_value=None))


    def resolve_Testcases(self, info,**kwargs):
        result=neo4jModels.Testcase().all

        if(kwargs.get('testcaseid')):
            result=neo4jModels.Testcase.match(neo4jModels.graph).where(testcaseid='t'+kwargs.get('testcaseid'))#type=TestcaseMatch
        return [TestcaseSchema2(**testcase.as_dict()) for testcase in result]

    def resolve_Lines(self, info,**kwargs):
        result = neo4jModels.Line().all

        if (kwargs.get('lineid')):
            result = neo4jModels.Line.match(neo4jModels.graph).where(
                lineid=kwargs.get('lineid'))  # type=LineMatch
        return [LineSchema2(**line.as_dict()) for line in result]
        #return [LineSchema(**line.as_dict()) for line in neo4jModels.Line().all]

schema2 = graphene.Schema(query=Query2)