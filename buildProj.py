import os
import subprocess
import configparser
import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists
cf = configparser.ConfigParser()
cf.read('config.ini')

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:313461@127.0.0.1:3306/spider-worker'
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def build(git):
    tacocopath = cf.get('filepath', 'tacoco-path')
    name = git.split('/')[-1].split('.')[0]
    projpath = '/home/dongxinxiang/demo/' + name
    commit = subprocess.Popen('git ls-remote ' + git + ' HEAD', shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode().split('\t')[0]
    exist = True
    if session.query(exists().where(models.Project.projectLink==git)).scalar()==False:
        newProj = models.Project(projectName=name, projectLink=git)
        session.add(newProj)
        session.commit()
        exist=False
    projId = session.query(models.Project).filter(models.Project.projectLink == git).one().projectId
    buildQuery=session.query(models.Build).filter(models.Build.commitId==commit,models.Build.projectId==projId)
    if session.query(buildQuery.exists()).scalar() == False:
        newBuild=models.Build(commitId=commit,projectId=projId)
        session.add(newBuild)
        session.commit()
        exist=False
        op = 'git clone ' + git + ' ' + projpath
        os.system(op)

        scriptpath = cf.get('filepath', 'run-tacoco-path')
        os.chdir(projpath)
        os.system('mvn compile test-compile')
        command = scriptpath + ' ' + projpath + ' ' + tacocopath
        os.system(command)
    buildId=session.query(models.Build).filter(models.Build.commitId == commit,models.Build.projectId==projId).one().buildId

    return exist,buildId,projId,name


build('https://github.com/spideruci/Tarantula.git')

#

#s=os.system('git ls-remote https://github.com/sunflower0309/jsoup.git HEAD')



# tacocopath = cf.get('filepath', 'tacoco-path')
# projpath = cf.get('filepath', 'project-path')
# scriptpath = cf.get('filepath', 'run-tacoco-path')
# os.chdir(projpath)
# os.system('mvn compile test-compile')
# command = scriptpath + ' ' + projpath + ' ' + tacocopath
# print(command)
# os.system(command)
#os.system('/home/dongxinxiang/tacoco/scripts/run-tacoco /home/dongxinxiang/commons-io /home/dongxinxiang/tacoco')
#'/home/dongxinxiang/tacoco/scripts/run-tacoco /home/dongxinxiang/commons-io /home/dongxinxiang/tacoco'