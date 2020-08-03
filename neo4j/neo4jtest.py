from py2neo import Graph,NodeMatcher
from py2neo.ogm import GraphObject, Property, RelatedTo,RelatedFrom


class Testcase(GraphObject):
    __primarykey__ = 'id'
    testcaseid=Property()
    coverage=RelatedTo('Line','Cover')
    def as_dict(self):
        return {
            'id': self.testcaseid
        }

    def fetch(self,id):
        nodematcher = NodeMatcher(graph)
        return nodematcher.match('Testcase').where(testcaseid=id).first()

    def fetch_coverage(self):
        return self.coverage._related_objects

class Line(GraphObject):
    lineid=Property()
    covered=RelatedFrom('Testcase','Cover')
    def fetch(self,id):
        return self.match(graph).where(lineid=id)

    def as_dict(self):
        return {
            'lineid': self.lineid,
            'covered': self.covered
        }
    def fetch_covered(self):
        return [{
            **testcase[0].as_dict()
        } for testcase in self.covered._related_objects]
graph = Graph("http://localhost:7474",auth=("neo4j","313461"))
nodematcher=NodeMatcher(graph)
findnode=nodematcher.match('Testcase').where(id='10357').first()
#
#
# result=neo4jModels.Testcase().all
# rr=[neo4jSchema.TestcaseSchema(testcase) for testcase in result]
#[TestcaseSchema(**testcase.as_dict()) for testcase in result]
# result=neo4jModels.Testcase().match(graph).where(id='10357')#type = testcasematch, list of testcase
# result1=neo4jModels.Testcase().match(graph)
# result2=neo4jModels.Testcase().all
# rr=[neo4jSchema.TestcaseSchema(**testcase.as_dict()) for testcase in result]#type = TestcaseSchema, list of testcaseschema
# rr1=[neo4jSchema.TestcaseSchema(**testcase.as_dict()) for testcase in result1]
# rr2=[neo4jSchema.TestcaseSchema(**testcase.as_dict()) for testcase in result2]
# print(rr)
# print(rr1)
# print(rr2)
# print(type(result))
# for i in rr:
#     print(type(i))
# for t in Testcase.match(graph).where(id='10357'):
#     print(type(t))#type=testcase
#     for lines in t.fetch_coverage():
#         print(type(lines[0]))
#         print(neo4jSchema.LineSchema(**lines[0].as_dict()))
#     print(type(neo4jSchema.TestcaseSchema(t)))#testcase schema

t=Line.match(graph).where(lineid='71614').first()
print([{**testcase[0].as_dict()} for testcase in t.covered._related_objects])#type=testcase
# for lines in t.fetch_covered():
#     print(lines)
    #print(neo4jSchema.TestcaseSchema(**lines[0].as_dict()))
#print(type(neo4jSchema2.TestcaseSchema2(t)))#testcase schema

# t=Testcase.match(graph).where(testcaseid='t10357').first()
# print(type(t))#type=testcase
# for lines in t.fetch_coverage():
#     print(type(lines[0]))
#     print(neo4jSchema2.LineSchema2(**lines[0].as_dict()))
# print(type(neo4jSchema.TestcaseSchema(t)))#testcase schema
# for i in list(graph.match([findnode])):
#     print()
#print(list(graph.match([findnode])))
# for x in t1.coverage:
#     print(x.id)