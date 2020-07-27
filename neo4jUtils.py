from py2neo import Graph,Node,Subgraph
import json
import models
import pandas as pd

graph = Graph("http://localhost:7474",auth=("neo4j","313461"))

# testcase = Node("Testcase",id = "12")
# line = Node("Line",id = "12")
# graph.create(testcase)
# graph.create(line)
#
# relation = Relationship(testcase, "Covered", line)
# graph.create(relation)
# li=['Testcase','Line']
# print(list(graph.nodes.match('Line')))

def database_operation(projectId,buildId,jsonpath,session):
    f = open(jsonpath, 'r', encoding='utf-8')
    dict_data = json.load(f)
    sourceList = dict_data['sources']
    testList = dict_data['testsIndex']
    testList.pop(-1)
    tx1 = graph.begin()

    testIdDict = {}  # only one query, put it in the dict, less connect to database
    testIdandLines = {}
    testIdList = []
    neoTestList=[]
    currTestListplusId = session.query(models.TestCase).filter(models.TestCase.projectId == projectId,
                                                               models.TestCase.buildId == buildId).all()
    for cases in currTestListplusId:
        string = cases.sourceName + cases.signature
        testIdDict[string] = cases.testcaseId
        testIdandLines[cases.testcaseId] = []
        testIdList.append(cases.testcaseId)
        testcase = Node("Testcase", testcaseid=str(cases.testcaseId))
        neoTestList.append(testcase)

    neoTestList = Subgraph(neoTestList)
    tx1.create(neoTestList)
    tx1.commit()

    tx2 = graph.begin()
    lineIdDict = {}
    lineIdandTestcases = {}
    lineIdList = []
    neoLineList=[]
    currLineListplusId = session.query(models.Line).filter(models.Line.projectId == projectId,
                                                           models.Line.buildId == buildId).all()
    for lines in currLineListplusId:
        string = lines.sourceName + str(lines.lineNumber)
        lineIdDict[string] = lines.lineId
        lineIdandTestcases[lines.lineId] = []
        lineIdList.append(lines.lineId)
        line = Node("Line", lineid=str(lines.lineId))
        neoLineList.append(line)

    neoLineList=Subgraph(neoLineList)
    tx2.create(neoLineList)
    tx2.commit()

    # for src in sourceList:
    #     fullname = src['source']['fullName'].replace('/', '.')
    #     startLine = src['source']['firstLine']
    #     activeTests = src['activatingTests']  # index in the list
    #     testcaseindex = 0
    #     for tests in activeTests:
    #         matrix = src['testStmtMatrix'][testcaseindex]  # single matrix
    #         testcaseinfo = testList[tests]
    #         testcaseId = testIdDict[testcaseinfo.split('/')[1] + testcaseinfo.split('/', 2)[-1]]
    #         for l in range(len(matrix)):
    #             if matrix[l] == True:
    #                 lineId = lineIdDict[fullname + str(l + startLine)]
    #                 graph.run("MATCH (t:Testcase),(l:Line) WHERE t.id ='"+ str(testcaseId) +"' AND l.id='"+str(lineId)+"' CREATE (t)-[:Cover]->(l)")
    #     print(fullname + ' success!')


#print(list(graph.run("MATCH (n:Testcase) RETURN n LIMIT 25")))

#database_operation(17,25,'/home/dongxinxiang/demo/tacoco_output/Tarantula-cov-matrix.json',workerServer.session)
#database_operation(7,34,'/home/dongxinxiang/demo/tacoco_output/jsoup-cov-matrix.json',workerServer.session)
import pymysql
import csv
def make_csv(x,y):
    conn = pymysql.connect(
        host='127.0.0.1',port=3306,
    user ='root', password ='313461',
    database ='spider-worker')
    cursor = conn.cursor()
    # sql='select testcaseId from testcase;'
    # cursor.execute(sql)
    # testcases=cursor.fetchall()
    # tt=[['t'+str(list(t)[0])]+['Testcase'] for t in testcases]
    # l1 = ['testcaseid:ID', ':LABEL']
    # file1 = pd.DataFrame(data=tt, columns=l1)
    # file1.to_csv('/home/dongxinxiang/testcase.csv')
    #print(tt[0:3])



    # sql2 = 'select lineId from line;'
    # cursor.execute(sql2)
    # lines=cursor.fetchall()
    # ll=[[str(list(l)[0])]+['Line'] for l in lines]

    # milestone=[19279,29279,39279,49279,59279,69279,79279,89279,95502]
    # for x in range(len(milestone)-1):
    #     sql='select * from coverage where testcaseid>'+str(milestone[x])+' and testcaseid<='+str(milestone[x+1])
    #     cursor.execute(sql)
    #     cov = cursor.fetchall()
    #     cc = [['t' + str(list(c)[1]), str(list(c)[0])] + ['Cover'] for c in cov]
    #     print(len(cc))
    sql3 = 'select * from coverage where testcaseid>'+str(x)+' and testcaseid<='+str(y)
    cursor.execute(sql3)
    cov = cursor.fetchall()
    cc=[['t'+str(list(c)[1]),str(list(c)[0])]+['Cover'] for c in cov]
    print(len(cc))
    l1 = [':START_ID', ':END_ID',':TYPE']
    with open('/home/dongxinxiang/cov.csv', 'a+', newline='') as file:
        writer = csv.writer(file)
        #writer.writerow(l1)
        writer.writerows(cc)
# make_csv(39279,49279)
# make_csv(49279,59279)
# make_csv(59279,69279)
# make_csv(69279,79279)
# make_csv(79279,89279)
# make_csv(89279,95502)