from py2neo import Graph
from py2neo.ogm import GraphObject,Property,RelatedFrom,RelatedTo

graph = Graph("http://172.17.0.1:7474",auth=("neo4j","313461"))

class Testcase(GraphObject):
    __primarykey__ = 'id'
    testcaseid=Property()
    coverage=RelatedTo('Line','Cover')
    def as_dict(self):
        return {
            'id': self.testcaseid
        }

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
t=Line.match(graph).where(lineid='71614').first()
print([{**testcase[0].as_dict()} for testcase in t.covered._related_objects])#type=testcase