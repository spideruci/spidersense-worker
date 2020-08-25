import configparser
from src import models
from sqlalchemy import exists
from src import sqlsession



session = sqlsession.session

def build(git,commit,time,committer,message):
    name = git.split('/')[-1].split('.')[0]

    exist = True
    if session.query(exists().where(models.Project.projectLink == git)).scalar()==False:
        newProj = models.Project(projectName=name, projectLink=git)
        session.add(newProj)
        session.commit()
        exist=False
    projId = session.query(models.Project).filter(models.Project.projectLink == git).one().projectId
    buildQuery=session.query(models.Build).filter(models.Build.commitId == commit, models.Build.projectId == projId)
    if session.query(buildQuery.exists()).scalar() == False:
        newBuild= models.Build(commitId=commit, projectId=projId, timestamp=time,committer=committer,message=message)
        session.add(newBuild)
        session.commit()
        exist=False
    buildId=session.query(models.Build).filter(models.Build.commitId == commit, models.Build.projectId == projId).one().buildId

    return exist,buildId,projId,name
