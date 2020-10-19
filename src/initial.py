from src import workerServer,utils,utilsfordocker
import time
import docker
from concurrent.futures import ThreadPoolExecutor
# workerServer.operate_proj('https://github.com/sunflower0309/gson.git','ebd311ff5467a4909163a20212a284bcf1824023',utils.githubTimeConvert('2020-07-29T09:59:24Z'))
# workerServer.operate_proj('https://github.com/sunflower0309/gson.git','acb8361f7a0bbf399b9ec81beb219cc40b22a07c',utils.githubTimeConvert('2020-07-29T07:28:50Z'))
# workerServer.operate_proj('https://github.com/sunflower0309/jsoup.git','dc38b0aed68f0ece00a32dd927e56c4e50132ed9'
#                           ,utils.githubTimeConvert('2020-07-20T21:36:02Z'))
# workerServer.operate_proj('https://github.com/spideruci/Tarantula.git','7882a7c1925ae5092fade009fc7cc9f39309da82',
#                           utils.githubTimeConvert('2015-06-02T21:36:02Z'),'VijayKrishna Palepu','Using the PassFailPair\'s in the Localizer\'s API.')
# workerServer.operate_proj('https://github.com/spideruci/Tarantula.git','b9518b0e4a9e5872824e25a290f2f04a72991f1c',
#                           utils.githubTimeConvert('2015-06-03T03:00:13Z'),'VijayKrishna Palepu','Basic DataBuilder tests.')
# import requests
# print(requests.get('https://api.github.com/rate_limit',headers=utils.headers).json())
# requests.get('https://api.github.com/repos/'+'sunflower0309'+'/'+'commons-io'+'/branches',headers=utils.headers).json()
# print(requests.get('https://api.github.com/rate_limit',headers=utils.headers).json())
#workerServer.poll()
#utilsfordocker.database_operation(74,246,'/home/dongxinxiang/tacoco/tacoco_output/mid_example-cov-matrix.json')
#utils.getAllCommits()
#workerServer.dockercheck()
#print(workerServer.client.containers(all=True)[0]['Id'])
# print(time.time())
# print(utils.getNewProjcommits('apache','flink'))
# for i in range(86001,86085):
#     print(str(i)+',')