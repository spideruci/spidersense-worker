from graphql import GraphQLError
from py2neo import Graph,NodeMatcher
from py2neo.ogm import GraphObject, Property, RelatedTo,RelatedFrom
graph = Graph("http://localhost:7474",auth=("neo4j","313461"))
class BaseModel(GraphObject):
    """
    Implements some basic functions to guarantee some standard functionality
    across all models. The main purpose here is also to compensate for some
    missing basic features that we expected from GraphObjects, and improve the
    way we interact with them.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def all(self):
        return self.match(graph)

    def save(self):
        graph.push(self)


class Testcase(BaseModel):
    testcaseid=Property()
    coverage=RelatedTo('Line','Cover')
    def as_dict(self):
        return {
            'testcaseid': self.testcaseid,
            'coverage':self.coverage
        }

    def fetch(self,id):
        self.match(graph).where(testcaseid=id)

    def fetch_coverage(self):
        return [{
            **line[0].as_dict()
        } for line in self.coverage._related_objects]

class Line(BaseModel):
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

