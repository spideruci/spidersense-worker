import os
import subprocess
import configparser

cf = configparser.ConfigParser()
cf.read('config.ini')

tacocopath = cf.get('filepath', 'tacoco-path')
projpath = cf.get('filepath', 'project-path')
scriptpath = cf.get('filepath', 'run-tacoco-path')
os.chdir(projpath)
os.system('mvn compile test-compile')
command = scriptpath+' '+projpath+' '+tacocopath
print(command)
os.system(command)
#os.system('/home/dongxinxiang/tacoco/scripts/run-tacoco /home/dongxinxiang/commons-io /home/dongxinxiang/tacoco')
#'/home/dongxinxiang/tacoco/scripts/run-tacoco /home/dongxinxiang/commons-io /home/dongxinxiang/tacoco'